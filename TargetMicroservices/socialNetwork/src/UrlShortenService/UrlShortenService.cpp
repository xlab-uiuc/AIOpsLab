#include <signal.h>
#include <thrift/protocol/TBinaryProtocol.h>
#include <thrift/server/TThreadedServer.h>
#include <thrift/transport/TBufferTransports.h>
#include <thrift/transport/TServerSocket.h>

#include <opentelemetry/logs/provider.h>
#include <opentelemetry/context/runtime_context.h>

#include "../utils.h"
#include "../utils_memcached.h"
#include "../utils_mongodb.h"
#include "../utils_thrift.h"
#include "UrlShortenHandler.h"
#include "nlohmann/json.hpp"


using apache::thrift::protocol::TBinaryProtocolFactory;
using apache::thrift::server::TThreadedServer;
using apache::thrift::transport::TFramedTransportFactory;
using apache::thrift::transport::TServerSocket;
using namespace social_network;

static memcached_pool_st* memcached_client_pool;
static mongoc_client_pool_t* mongodb_client_pool;


void sigintHandler(int sig) {
  if (memcached_client_pool != nullptr) {
    memcached_pool_destroy(memcached_client_pool);
  }
  if (mongodb_client_pool != nullptr) {
    mongoc_client_pool_destroy(mongodb_client_pool);
  }
  exit(EXIT_SUCCESS);
}

int main(int argc, char* argv[]) {
  signal(SIGINT, sigintHandler);
  init_logger();
  SetUpTracer("config/jaeger-config.yml", "url-shorten-service");
  // Set up otel tracer
  SetUpOpenTelemetryTracer("url-shorten-service");
  SetUpOpenTelemetryLogger("url-shorten-service");

  // auto prop         = opentelemetry::context::propagation::GlobalTextMapPropagator::GetGlobalPropagator();
  // auto orig_ctx     = opentelemetry::context::RuntimeContext::GetCurrent();
  // auto prev_ctx     = prop->Extract(otel_carrier_reader, orig_ctx);

  auto logger = opentelemetry::logs::Provider::GetLoggerProvider()->GetLogger(
        "url-shorten-service");
  auto tracer = opentelemetry::trace::Provider::GetTracerProvider()->GetTracer("url-shorten-service");
  auto ctx  = tracer->GetCurrentSpan()->GetContext();

  json config_json;
  if (load_config_file("config/service-config.json", &config_json) != 0) {
    exit(EXIT_FAILURE);
  }
  int port = config_json["url-shorten-service"]["port"];

  int mongodb_conns = config_json["url-shorten-mongodb"]["connections"];
  int mongodb_timeout = config_json["url-shorten-mongodb"]["timeout_ms"];

  int memcached_conns = config_json["url-shorten-memcached"]["connections"];
  int memcached_timeout = config_json["url-shorten-memcached"]["timeout_ms"];

  memcached_client_pool = init_memcached_client_pool(config_json, "url-shorten",
                                                     32, memcached_conns);
  mongodb_client_pool =
      init_mongodb_client_pool(config_json, "url-shorten", mongodb_conns);
  if (memcached_client_pool == nullptr || mongodb_client_pool == nullptr) {
    return EXIT_FAILURE;
  }

  mongoc_client_t* mongodb_client = mongoc_client_pool_pop(mongodb_client_pool);
  if (!mongodb_client) {
    LOG(fatal) << "Failed to pop mongoc client";
    logger->EmitLogRecord(opentelemetry::logs::Severity::kFatal, "Failed to pop mongoc client", 
                      ctx.trace_id(), ctx.span_id(), ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
    return EXIT_FAILURE;
  }
  bool r = false;
  while (!r) {
    r = CreateIndex(mongodb_client, "url-shorten", "shortened_url", true);
    if (!r) {
      LOG(error) << "Failed to create mongodb index, try again";
      logger->EmitLogRecord(opentelemetry::logs::Severity::kError, "Failed to create mongodb index, try again", 
                      ctx.trace_id(), ctx.span_id(), ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
      sleep(1);
    }
  }
  mongoc_client_pool_push(mongodb_client_pool, mongodb_client);

  std::mutex thread_lock;
  std::shared_ptr<TServerSocket> server_socket = get_server_socket(config_json, "0.0.0.0", port);
  TThreadedServer server(
      std::make_shared<UrlShortenServiceProcessor>(
          std::make_shared<UrlShortenHandler>(
              memcached_client_pool, mongodb_client_pool, &thread_lock)),
      server_socket,
      std::make_shared<TFramedTransportFactory>(),
      std::make_shared<TBinaryProtocolFactory>());

  LOG(info) << "Starting the url-shorten-service server...";
  
  logger->EmitLogRecord(opentelemetry::logs::Severity::kInfo, "Starting the url-shorten-service server...", ctx.trace_id(),
                      ctx.span_id(), ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
  server.serve();
}