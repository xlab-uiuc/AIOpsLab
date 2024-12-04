# Portions Copyright (c) Microsoft Corporation
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for full license information.

FROM yg397/thrift-microservice-deps:xenial AS builder

ARG LIB_REDIS_PLUS_PLUS_VERSION=1.2.3

# Remove the existing CMake
RUN apt-get remove --purge --auto-remove -y cmake

# Install required tools and add Kitware's repository
RUN apt-get update && apt-get install -y \
    software-properties-common \
    lsb-release \
    apt-transport-https \
    wget \
    gnupg \
    libcurl4-gnutls-dev \
    build-essential \
    autoconf \
    libtool \
    pkg-config \
    libsystemd-dev \
    libc-ares-dev 

# Add Kitware's GPG key
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null

RUN echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/kitware.list

RUN apt-get update && apt-get install -y cmake

RUN add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get install -y gcc-7 g++-7

RUN wget https://github.com/google/googletest/archive/refs/tags/v1.14.0.tar.gz \
    && tar -xzf v1.14.0.tar.gz \
    && cd googletest-1.14.0 \
    && cmake . -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

RUN wget https://github.com/google/benchmark/archive/refs/tags/v1.8.3.tar.gz \
    && tar -xzf v1.8.3.tar.gz \
    && cd benchmark-1.8.3 \
    && cmake . -DGOOGLETEST_PATH=`realpath ../googletest-1.14.0` -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

RUN wget https://github.com/abseil/abseil-cpp/archive/refs/tags/20230802.1.tar.gz \
    && tar zxf 20230802.1.tar.gz \
    && cd abseil-cpp-20230802.1 \
    && cmake . -DCMAKE_CXX_STANDARD=11 -DABSL_ENABLE_INSTALL=TRUE -DABSL_USE_EXTERNAL_GOOGLETEST=ON -DABSL_PROPAGATE_CXX_STD=TRUE -DABSL_BUILD_TEST_HELPERS=OFF -DABSL_BUILD_TESTING=OFF -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

RUN wget https://github.com/protocolbuffers/protobuf/archive/refs/tags/v25.1.tar.gz \
    && tar zxf v25.1.tar.gz \
    && cd protobuf-25.1 \
    && cmake -Dprotobuf_DISABLE_RTTI=ON -Dprotobuf_WITH_ZLIB=ON -Dprotobuf_ABSL_PROVIDER=package -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -Dprotobuf_BUILD_TESTS=OFF -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

# Dependency needed by grpc
RUN wget --no-check-certificate https://c-ares.org/download/c-ares-1.25.0.tar.gz \
    && tar zxf c-ares-1.25.0.tar.gz \
    && cd c-ares-1.25.0 \
    && cmake -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

RUN wget https://github.com/google/re2/archive/refs/tags/2023-11-01.tar.gz \ 
    && tar zxf 2023-11-01.tar.gz \
    && cd re2-2023-11-01 \
    && cmake -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

RUN wget https://github.com/grpc/grpc/archive/refs/tags/v1.60.0.tar.gz \
    && tar zxf v1.60.0.tar.gz \
    && cd grpc-1.60.0 \
    && cmake . -DgRPC_INSTALL=ON -DCMAKE_BUILD_TYPE=Release -DgRPC_PROTOBUF_PROVIDER=package -DgRPC_RE2_PROVIDER=package -DCMAKE_DISABLE_FIND_PACKAGE_systemd=ON -DgRPC_ZLIB_PROVIDER=package -DgRPC_SSL_PROVIDER=package -DgRPC_CARES_PROVIDER=package -DgRPC_ABSL_PROVIDER=package -DCMAKE_C_FLAGS='-fPIC' -DCMAKE_CXX_FLAGS='-fPIC -std=gnu++11' -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 \
    && cmake --build . --target install -- -j`nproc`

# Download and extract OpenTelemetry C++ source
WORKDIR /tmp
RUN wget https://github.com/open-telemetry/opentelemetry-cpp/archive/refs/tags/v1.13.0.tar.gz \
    && tar -xzf v1.13.0.tar.gz \
    && mv opentelemetry-cpp-1.13.0 opentelemetry-cpp \
    && rm v1.13.0.tar.gz
# RUN wget https://github.com/open-telemetry/opentelemetry-cpp/archive/refs/tags/v1.13.0.tar.gz \
#     && tar -xzf v1.13.0.tar.gz \
#     && mv opentelemetry-cpp-1.13.0 opentelemetry-cpp \
#     && rm v1.13.0.tar.gz

########## Apply a patch for the otel-cpp-1.9.1 which supports jaeger exporter ##########
# Build OpenTelemetry C++
WORKDIR /tmp/opentelemetry-cpp
# RUN <<EOR
# cat << 'EOF' > fix2.patch
# diff --git a/api/include/opentelemetry/trace/propagation/detail/hex.h b/api/include/opentelemetry/trace/propagation/detail/hex.h
# index c8bd58f8..aecdeddd 100644
# --- a/api/include/opentelemetry/trace/propagation/detail/hex.h
# +++ b/api/include/opentelemetry/trace/propagation/detail/hex.h
# @@ -5,6 +5,7 @@

#  #include <algorithm>
#  #include <cstring>
# +#include <cstdint>

#  #include "opentelemetry/nostd/string_view.h"
#  #include "opentelemetry/version.h"
# diff --git a/exporters/jaeger/src/THttpTransport.h b/exporters/jaeger/src/THttpTransport.h
# index 9c796e67..eec24f34 100644
# --- a/exporters/jaeger/src/THttpTransport.h
# +++ b/exporters/jaeger/src/THttpTransport.h
# @@ -20,7 +20,7 @@ class THttpTransport : public apache::thrift::transport::TVirtualTransport<THttp
#    THttpTransport(std::string endpoint, ext::http::client::Headers extra_headers);
#    ~THttpTransport() override;

# -  bool isOpen() const override;
# +  bool isOpen() const;

#    uint32_t read(uint8_t *buf, uint32_t len);

# diff --git a/exporters/jaeger/src/TUDPTransport.cc b/exporters/jaeger/src/TUDPTransport.cc
# index e4111273..a3aaded2 100644
# --- a/exporters/jaeger/src/TUDPTransport.cc
# +++ b/exporters/jaeger/src/TUDPTransport.cc
# @@ -2,6 +2,7 @@
#  // SPDX-License-Identifier: Apache-2.0

#  #include <sstream>  // std::stringstream
# +#include <unistd.h>

#  #include "TUDPTransport.h"
#  #include "opentelemetry/sdk_config.h"
# diff --git a/exporters/jaeger/src/TUDPTransport.h b/exporters/jaeger/src/TUDPTransport.h
# index df3151d1..c2c6f467 100644
# --- a/exporters/jaeger/src/TUDPTransport.h
# +++ b/exporters/jaeger/src/TUDPTransport.h
# @@ -28,7 +28,7 @@ class TUDPTransport : public apache::thrift::transport::TVirtualTransport<TUDPTr
#    TUDPTransport(const std::string &host, int port);
#    ~TUDPTransport() override;

# -  bool isOpen() const override;
# +  bool isOpen() const;

#    void open() override;
# EOF
# patch -p1 < fix2.patch
# rm fix2.patch
# EOR

RUN mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=ON -DCMAKE_CXX_FLAGS='-std=gnu++11 -fPIC' -DWITH_OTLP_HTTP=ON -DWITH_BENCHMARK=OFF -DBUILD_TESTING=OFF -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 -DWITH_ABSEIL=ON -DWITH_OTLP_GRPC=ON \
    && cmake --build . --target all -- -j`nproc` \
    && cmake --install .

# Apply patch and re-install Redis plus plus
RUN cd /tmp/redis-plus-plus\
&& sed -i '/Transaction transaction/i\\    ShardsPool* get_shards_pool(){\n        return &_pool;\n    }\n' \
   src/sw/redis++/redis_cluster.h \
&& cmake -DREDIS_PLUS_PLUS_USE_TLS=ON -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 . \
&& make -j$(nproc) \
&& make install

COPY ./ /social-network-microservices
RUN cd /social-network-microservices \
    && mkdir -p build \
    && cd build \
    # && cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 .. \
    && cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_CXX_COMPILER=g++-7 .. \
    && make -j`nproc` \
    && make install

FROM ubuntu:18.04

# Copy compiled C++ binaries and dependencies
COPY --from=builder /usr/local/bin/* /usr/local/bin/
COPY --from=builder /usr/local/lib/* /usr/local/lib/

# Install system dependencies
# iproute2 is for a chaos tool
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openssl \
        libssl1.0.0 \
        ca-certificates \
        libsasl2-2 \
        libmemcached11 \
        libmemcachedutil2 \
        iproute2 \
        libcurl3-gnutls \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /social-network-microservices
