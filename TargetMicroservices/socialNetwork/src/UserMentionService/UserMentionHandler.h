#ifndef SOCIAL_NETWORK_MICROSERVICES_SRC_USERMENTIONSERVICE_USERMENTIONHANDLER_H_
#define SOCIAL_NETWORK_MICROSERVICES_SRC_USERMENTIONSERVICE_USERMENTIONHANDLER_H_

#include <bson.h>
#include <libmemcached/memcached.h>
#include <libmemcached/util.h>
#include <mongoc.h>

#include <opentelemetry/trace/provider.h>
#include <opentelemetry/trace/tracer.h>
#include <opentelemetry/trace/span.h>
#include <opentelemetry/trace/scope.h>
#include <opentelemetry/trace/span_startoptions.h>
#include <opentelemetry/trace/propagation/http_trace_context.h>
#include <opentelemetry/context/runtime_context.h>
#include <opentelemetry/context/propagation/global_propagator.h>

#include "../../gen-cpp/UserMentionService.h"
#include "../../gen-cpp/social_network_types.h"
#include "../ClientPool.h"
#include "../logger.h"
#include "../tracing.h"
#include "../utils.h"

namespace social_network {

class UserMentionHandler : public UserMentionServiceIf {
 public:
  UserMentionHandler(memcached_pool_st *, mongoc_client_pool_t *);
  ~UserMentionHandler() override = default;

  void ComposeUserMentions(std::vector<UserMention> &_return, int64_t,
                           const std::vector<std::string> &,
                           const std::map<std::string, std::string> &) override;

 private:
  memcached_pool_st *_memcached_client_pool;
  mongoc_client_pool_t *_mongodb_client_pool;
};

UserMentionHandler::UserMentionHandler(
    memcached_pool_st *memcached_client_pool,
    mongoc_client_pool_t *mongodb_client_pool) {
  _memcached_client_pool = memcached_client_pool;
  _mongodb_client_pool = mongodb_client_pool;
}

void UserMentionHandler::ComposeUserMentions(
    std::vector<UserMention> &_return, int64_t req_id,
    const std::vector<std::string> &usernames,
    const std::map<std::string, std::string> &carrier) {
  opentelemetry::trace::StartSpanOptions options;
  OtelTextMapReader otel_carrier_reader(carrier);
  // Extract the context using the global propagator
  auto prop         = opentelemetry::context::propagation::GlobalTextMapPropagator::GetGlobalPropagator();
  auto orig_ctx     = opentelemetry::context::RuntimeContext::GetCurrent();
  auto prev_ctx     = prop->Extract(otel_carrier_reader, orig_ctx);
  options.parent    = opentelemetry::trace::GetSpan(prev_ctx)->GetContext();
 
  auto tracer           = opentelemetry::trace::Provider::GetTracerProvider()->GetTracer("user-mention-service");
  auto ospan            = tracer->StartSpan("compose_user_mentions_server", options);
  auto scoped_ospan     = tracer->WithActiveSpan(ospan);
  auto current_context  = opentelemetry::context::RuntimeContext::GetCurrent();
  auto span_ctx         = ospan->GetContext();

  auto logger       = opentelemetry::logs::Provider::GetLoggerProvider()->GetLogger("user-mention-service");

  // Initialize a span
  TextMapReader reader(carrier);
  std::map<std::string, std::string> writer_text_map;
  TextMapWriter writer(writer_text_map);
  auto parent_span = opentracing::Tracer::Global()->Extract(reader);
  auto span = opentracing::Tracer::Global()->StartSpan(
      "compose_user_mentions_server",
      {opentracing::ChildOf(parent_span->get())});
  opentracing::Tracer::Global()->Inject(span->context(), writer);

  std::vector<UserMention> user_mentions;
  if (!usernames.empty()) {
    std::map<std::string, bool> usernames_not_cached;

    for (auto &username : usernames) {
      usernames_not_cached.emplace(std::make_pair(username, false));
    }

    // Find in Memcached
    memcached_return_t rc;
    auto client = memcached_pool_pop(_memcached_client_pool, true, &rc);
    if (!client) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
      se.message = "Failed to pop a client from memcached pool";
      logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, span_ctx.trace_id(),
                      span_ctx.span_id(), span_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
      throw se;
    }

    char **keys;
    size_t *key_sizes;
    keys = new char *[usernames.size()];
    key_sizes = new size_t[usernames.size()];
    int idx = 0;
    for (auto &username : usernames) {
      std::string key_str = username + ":user_id";
      keys[idx] = new char[key_str.length() + 1];
      strcpy(keys[idx], key_str.c_str());
      key_sizes[idx] = key_str.length();
      idx++;
    }

    // auto parent_context        = opentelemetry::context::RuntimeContext::Attach(current_context);
    auto get_ospan             = tracer->StartSpan("compose_user_mentions_memcached_get_client");
    auto get_scoped_ospan      = tracer->WithActiveSpan(get_ospan);
    auto get_ospan_ctx         = get_ospan->GetContext();

    auto get_span = opentracing::Tracer::Global()->StartSpan(
        "compose_user_mentions_memcached_get_client",
        {opentracing::ChildOf(&span->context())});
    rc = memcached_mget(client, keys, key_sizes, usernames.size());
    if (rc != MEMCACHED_SUCCESS) {
      LOG(error) << "Cannot get usernames of request " << req_id << ": "
                 << memcached_strerror(client, rc);
      std::string msg = "Cannot get usernames of request " + std::to_string(req_id) + ": " +
           memcached_strerror(client, rc);
      logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      msg, get_ospan_ctx.trace_id(),
                      get_ospan_ctx.span_id(), get_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
      ServiceException se;
      se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
      se.message = memcached_strerror(client, rc);
      memcached_pool_push(_memcached_client_pool, client);
      get_span->Finish();
      get_ospan->End();
      throw se;
    }

    char return_key[MEMCACHED_MAX_KEY];
    size_t return_key_length;
    char *return_value;
    size_t return_value_length;
    uint32_t flags;

    while (true) {
      return_value = memcached_fetch(client, return_key, &return_key_length,
                                     &return_value_length, &flags, &rc);
      if (return_value == nullptr) {
        LOG(debug) << "Memcached mget finished "
                   << memcached_strerror(client, rc);
        std::string msg = "Memcached mget finished " + std::string(memcached_strerror(client, rc));
        logger->EmitLogRecord(opentelemetry::logs::Severity::kDebug, 
                      msg, get_ospan_ctx.trace_id(),
                      get_ospan_ctx.span_id(), get_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
        break;
      }
      if (rc != MEMCACHED_SUCCESS) {
        free(return_value);
        memcached_quit(client);
        memcached_pool_push(_memcached_client_pool, client);
        LOG(error) << "Cannot get components of request " << req_id;
        std::string msg = "Cannot get components of request " + req_id;
        logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      msg, get_ospan_ctx.trace_id(),
                      get_ospan_ctx.span_id(), get_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
        ServiceException se;
        se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
        se.message =
            "Cannot get usernames of request " + std::to_string(req_id);
        logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, get_ospan_ctx.trace_id(),
                      get_ospan_ctx.span_id(), get_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
        get_span->Finish();
        get_ospan->End();
        throw se;
      }
      UserMention new_user_mention;
      std::string username(return_key, return_key + return_key_length);
      username =
          username.substr(0, username.length() - std::strlen(":user_id"));
      new_user_mention.username = username;
      new_user_mention.user_id = std::stoul(
          std::string(return_value, return_value + return_value_length));
      user_mentions.emplace_back(new_user_mention);
      usernames_not_cached.erase(username);
      free(return_value);
    }
    memcached_quit(client);
    memcached_pool_push(_memcached_client_pool, client);
    get_span->Finish();
    get_ospan->End();
    for (int i = 0; i < usernames.size(); ++i) {
      delete keys[i];
    }
    delete[] keys;
    delete[] key_sizes;

    // Find the rest in MongoDB
    if (!usernames_not_cached.empty()) {
      auto find_ospan            = tracer->StartSpan("compose_user_mentions_mongo_find_client");
      auto find_scoped_ospan     = tracer->WithActiveSpan(find_ospan);
      auto find_ospan_ctx        = find_ospan->GetContext();

      mongoc_client_t *mongodb_client =
          mongoc_client_pool_pop(_mongodb_client_pool);
      if (!mongodb_client) {
        ServiceException se;
        se.errorCode = ErrorCode::SE_MONGODB_ERROR;
        se.message = "Failed to pop a client from MongoDB pool";
        logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, find_ospan_ctx.trace_id(),
                      find_ospan_ctx.span_id(), find_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
        throw se;
      }

      auto collection =
          mongoc_client_get_collection(mongodb_client, "user", "user");
      if (!collection) {
        ServiceException se;
        se.errorCode = ErrorCode::SE_MONGODB_ERROR;
        se.message = "Failed to create collection user from DB user";
        logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, find_ospan_ctx.trace_id(),
                      find_ospan_ctx.span_id(), find_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        throw se;
      }

      bson_t *query = bson_new();
      bson_t query_child_0;
      bson_t query_username_list;
      const char *key;
      idx = 0;
      char buf[16];

      BSON_APPEND_DOCUMENT_BEGIN(query, "username", &query_child_0);
      BSON_APPEND_ARRAY_BEGIN(&query_child_0, "$in", &query_username_list);
      for (auto &item : usernames_not_cached) {
        bson_uint32_to_string(idx, &key, buf, sizeof buf);
        BSON_APPEND_UTF8(&query_username_list, key, item.first.c_str());
        idx++;
      }
      bson_append_array_end(&query_child_0, &query_username_list);
      bson_append_document_end(query, &query_child_0);
      
      auto find_span = opentracing::Tracer::Global()->StartSpan(
          "compose_user_mentions_mongo_find_client",
          {opentracing::ChildOf(&span->context())});
      mongoc_cursor_t *cursor =
          mongoc_collection_find_with_opts(collection, query, nullptr, nullptr);
      const bson_t *doc;

      while (mongoc_cursor_next(cursor, &doc)) {
        bson_iter_t iter;
        UserMention new_user_mention;
        if (bson_iter_init_find(&iter, doc, "user_id")) {
          new_user_mention.user_id = bson_iter_value(&iter)->value.v_int64;
        } else {
          ServiceException se;
          se.errorCode = ErrorCode::SE_MONGODB_ERROR;
          se.message = "Attribute of MongoDB item is not complete";
          logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, find_ospan_ctx.trace_id(),
                      find_ospan_ctx.span_id(), find_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
          bson_destroy(query);
          mongoc_cursor_destroy(cursor);
          mongoc_collection_destroy(collection);
          mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
          find_span->Finish();
          find_ospan->End();
          throw se;
        }
        if (bson_iter_init_find(&iter, doc, "username")) {
          new_user_mention.username = bson_iter_value(&iter)->value.v_utf8.str;
        } else {
          ServiceException se;
          se.errorCode = ErrorCode::SE_MONGODB_ERROR;
          se.message = "Attribute of MongoDB item is not complete";
          logger->EmitLogRecord(opentelemetry::logs::Severity::kError, 
                      se.message, find_ospan_ctx.trace_id(),
                      find_ospan_ctx.span_id(), find_ospan_ctx.trace_flags(),
                      opentelemetry::common::SystemTimestamp(std::chrono::system_clock::now()));
          bson_destroy(query);
          mongoc_cursor_destroy(cursor);
          mongoc_collection_destroy(collection);
          mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
          find_span->Finish();
          find_ospan->End();
          throw se;
        }
        user_mentions.emplace_back(new_user_mention);
      }
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      find_span->Finish();
      find_ospan->End();
    }
  }

  _return = user_mentions;
  span->Finish();
  ospan->End();
}

}  // namespace social_network

#endif  // SOCIAL_NETWORK_MICROSERVICES_SRC_USERMENTIONSERVICE_USERMENTIONHANDLER_H_
