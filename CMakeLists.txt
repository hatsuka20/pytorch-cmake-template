cmake_minimum_required(VERSION 3.4...3.18)
project(cmake_example)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_EXPORT_COMPILE_COMMANDS)
    add_custom_target(gen_compile_commands ALL
        COMMENT "Generating compile_commands.json")

    add_custom_command(
        TARGET gen_compile_commands
        PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove
        ${CMAKE_CURRENT_SOURCE_DIR}/compile_commands.json)

    add_custom_command(
        TARGET gen_compile_commands
        PRE_BUILD
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMAND
        ${CMAKE_COMMAND} -E create_symlink
        ${CMAKE_BINARY_DIR}/compile_commands.json
        ${CMAKE_CURRENT_SOURCE_DIR}/compile_commands.json
        COMMENT "Creating symbolic link")
endif()

find_package(Torch REQUIRED)

add_library(custom_class SHARED mylib/src/main.cpp)
target_link_libraries(custom_class "${TORCH_LIBRARIES}")
