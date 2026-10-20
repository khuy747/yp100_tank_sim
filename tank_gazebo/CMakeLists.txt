cmake_minimum_required(VERSION 3.8)
project(tank_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds
  DESTINATION share/${PROJECT_NAME}
)

# Optional models directory if present
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/models")
  install(
    DIRECTORY models
    DESTINATION share/${PROJECT_NAME}
  )
endif()

ament_package()
