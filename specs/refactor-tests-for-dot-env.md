# Plan to Fix Environment-Specific Tests

## 1. Understand the Current Configuration Approach

- The `Settings` class uses a default API key value (`test-key-e2e`)
- Environment variables can override this default value
- Tests expect to be able to control the API key through environment variable patching

## 2. Modify the Settings Class for Better Testability

1. **Add a Test Mode Flag**:
   - Add a class-level or instance-level flag to indicate when the Settings class is being used in tests
   - When in test mode, prioritize environment variables set by tests over any existing environment variables

2. **Improve Environment Variable Handling**:
   - Make the environment variable loading more explicit and controllable
   - Add a method to reset the settings to default values for testing

## 3. Update Test Files

### A. `test_config.py`

1. **Update `test_settings_creation_with_defaults`**:
   - Modify to expect the default API key value instead of requiring an environment variable
   - Use the new test mode flag to ensure environment variables are properly controlled

2. **Update `test_settings_with_environment_variables`**:
   - Ensure proper environment isolation before setting test variables
   - Use the test mode flag to ensure test environment variables take precedence

3. **Update `test_settings_required_fields`**:
   - Change the test to verify that the default value is used when no environment variable is provided
   - Remove the expectation that a ValueError will be raised

4. **Update `test_settings_partial_override`**:
   - Ensure proper environment isolation
   - Verify that specified values override defaults while unspecified values use defaults

5. **Update `test_settings_environment_prefix`**:
   - Ensure proper environment isolation
   - Verify that only properly prefixed variables are used

### B. `test_integration.py`

1. **Update `test_end_to_end_flow_with_mocked_api`**:
   - Use the test mode flag to ensure the test API key is used
   - Update assertions to match the expected behavior

2. **Update `test_configuration_loading_and_validation`**:
   - Use the test mode flag to ensure test environment variables take precedence
   - Update assertions to match the expected behavior

### C. `test_api_client.py`

1. **Fix `TestAviationStackClient` Tests**:
   - Update all test methods to use the test mode flag
   - Ensure proper environment isolation
   - Update assertions to match the expected behavior

## 4. Create a Test Environment Helper

1. **Create a Test Fixture**:
   - Implement a pytest fixture that sets up a clean test environment
   - The fixture should enable test mode and reset environment variables
   - Use this fixture in all environment-dependent tests

2. **Create a Context Manager**:
   - Implement a context manager for test environment setup/teardown
   - Use this in tests that need fine-grained control over the environment

## 5. Implementation Strategy

1. **Start with the Settings Class**:
   - Implement the test mode flag and improved environment handling
   - Add methods for resetting to defaults and controlling environment variable precedence

2. **Create Test Helpers**:
   - Implement the fixture and context manager for test environment control

3. **Update Tests Incrementally**:
   - Start with the simplest tests in `test_config.py`
   - Move on to integration tests
   - Finally, fix the API client tests

4. **Verify Each Step**:
   - Run tests after each change to ensure incremental progress
   - Use selective test running to focus on the tests being fixed

This plan aligns with the Test-Driven Development approach by focusing on incremental improvements while maintaining test coverage. It addresses the core issue of environment isolation in tests while preserving the practical usability of the configuration system.
