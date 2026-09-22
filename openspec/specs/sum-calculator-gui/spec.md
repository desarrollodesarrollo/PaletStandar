# sum-calculator-gui Specification

## Purpose

Provides a graphical desktop application that lets a user add two numbers together and see the result, distributable as a standalone executable that runs without a separate Python installation.

## Requirements

### Requirement: Sum two numbers via GUI
The system SHALL provide a graphical window with two input fields and a button that, when clicked, SHALL display the sum of the two input values.

#### Scenario: Adding two valid numbers
- **WHEN** the user enters `2` in the first field and `5` in the second field and clicks the "Sumar" button
- **THEN** the system displays the result `7`

#### Scenario: Adding decimal numbers
- **WHEN** the user enters `2.5` in the first field and `1.5` in the second field and clicks the "Sumar" button
- **THEN** the system displays the result `4.0`

### Requirement: Invalid input handling
The system SHALL validate that both input fields contain numeric values before computing a sum, and SHALL NOT crash on invalid input.

#### Scenario: Non-numeric input
- **WHEN** the user enters `abc` in either input field and clicks the "Sumar" button
- **THEN** the system displays an error message indicating the input is not a valid number, and does not close or crash

#### Scenario: Empty input
- **WHEN** the user clicks the "Sumar" button while one or both input fields are empty
- **THEN** the system displays an error message indicating a value is required, and does not close or crash

### Requirement: Standalone executable
The system SHALL be distributable as a standalone executable that launches the GUI application without requiring a separately installed Python interpreter or dependencies on the target machine.

#### Scenario: Launching the built executable
- **WHEN** the user runs the built executable file on a machine matching the build platform
- **THEN** the GUI calculator window opens, ready to accept input, without any additional setup steps
