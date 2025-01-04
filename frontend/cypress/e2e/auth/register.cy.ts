describe('User Registration', () => {
  beforeEach(() => {
    // Visit the registration page before each test
    cy.visit('/register');
  });

  it('should successfully register a new user', () => {
    // Generate a unique email using timestamp
    const timestamp = new Date().getTime();
    const testUser = {
      firstName: 'Test',
      lastName: 'User',
      email: `testuser${timestamp}@example.com`,
      password: 'Test@123',
    };

    // Fill out the registration form
    cy.get('input[name="firstName"]').type(testUser.firstName);
    cy.get('input[name="lastName"]').type(testUser.lastName);
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('input[name="confirmPassword"]').type(testUser.password);

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Should be redirected to login page with success message
    cy.url().should('include', '/login');
    cy.get('.MuiAlert-standardSuccess').should('exist');
  });

  it('should show error for mismatched passwords', () => {
    const testUser = {
      firstName: 'Test',
      lastName: 'User',
      email: 'testuser@example.com',
      password: 'Test@123',
    };

    // Fill out the form with mismatched passwords
    cy.get('input[name="firstName"]').type(testUser.firstName);
    cy.get('input[name="lastName"]').type(testUser.lastName);
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('input[name="confirmPassword"]').type('WrongPassword');

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Should show error message
    cy.get('.MuiAlert-standardError')
      .should('exist')
      .and('contain', 'Passwords do not match');
  });

  it('should show error for existing email', () => {
    const existingUser = {
      firstName: 'Test',
      lastName: 'User',
      email: 'existing@example.com',
      password: 'Test@123',
    };

    // Try to register with an existing email
    cy.get('input[name="firstName"]').type(existingUser.firstName);
    cy.get('input[name="lastName"]').type(existingUser.lastName);
    cy.get('input[name="email"]').type(existingUser.email);
    cy.get('input[name="password"]').type(existingUser.password);
    cy.get('input[name="confirmPassword"]').type(existingUser.password);

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Should show error message
    cy.get('.MuiAlert-standardError')
      .should('exist')
      .and('contain', 'Failed to create an account');
  });

  it('should validate required fields', () => {
    // Try to submit empty form
    cy.get('button[type="submit"]').click();

    // Check for HTML5 validation messages
    cy.get('input[name="firstName"]').should('have.attr', 'required');
    cy.get('input[name="lastName"]').should('have.attr', 'required');
    cy.get('input[name="email"]').should('have.attr', 'required');
    cy.get('input[name="password"]').should('have.attr', 'required');
    cy.get('input[name="confirmPassword"]').should('have.attr', 'required');
  });

  it('should navigate to login page', () => {
    // Click on the login link
    cy.contains('Already have an account?').click();
    cy.url().should('include', '/login');
  });
});
