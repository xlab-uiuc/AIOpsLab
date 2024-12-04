cmake_minimum_required(VERSION 3.5)
project(social_network_microservices)

find_package(opentelemetry-cpp CONFIG REQUIRED)
find_package(absl CONFIG REQUIRED)
find_package(protobuf CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "-O3")
set(CMAKE_INSTALL_PREFIX /usr/local/bin)

add_subdirectory(src)
#add_subdirectory(test)
#enable_testing()

include_directories(${OPENTELEMETRY_CPP_INCLUDE_DIRS})
link_libraries(${OPENTELEMETRY_CPP_LIBRARIES})

