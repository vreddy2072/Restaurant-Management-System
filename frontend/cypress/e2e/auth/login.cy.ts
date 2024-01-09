describe('User Login', () => {
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('/login');
  });

  it('should successfully login with valid credentials', () => {
    const testUser = {
      email: 'testuser@example.com',
      password: 'Test@123',
    };

    // Fill out the login form
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Should be redirected to menu page
    cy.url().should('include', '/menu');

    // Verify navigation bar shows logged-in state
    cy.get('button').contains('Logout').should('exist');
    cy.get('button').contains('Menu Management').should('exist');
  });

  it('should show error for invalid credentials', () => {
    const invalidUser = {
      email: 'wrong@example.com',
      password: 'WrongPassword',
    };

    // Fill out the form with invalid credentials
    cy.get('input[name="email"]').type(invalidUser.email);
    cy.get('input[name="password"]').type(invalidUser.password);

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Should show error message
    cy.get('.MuiAlert-standardError')
      .should('exist')
      .and('contain', 'Failed to sign in');
  });

  it('should validate required fields', () => {
    // Try to submit empty form
    cy.get('button[type="submit"]').click();

    // Check for HTML5 validation messages
    cy.get('input[name="email"]').should('have.attr', 'required');
    cy.get('input[name="password"]').should('have.attr', 'required');
  });

  it('should show loading state during login', () => {
    const testUser = {
      email: 'testuser@example.com',
      password: 'Test@123',
    };

    // Fill out the login form
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);

    // Submit and check for loading state
    cy.get('button[type="submit"]').click();
    cy.get('.MuiCircularProgress-root').should('exist');
  });

  it('should navigate to registration page', () => {
    // Click on the register link
    cy.contains("Don't have an account?").click();
    cy.url().should('include', '/register');
  });

  it('should maintain login state after page refresh', () => {
    const testUser = {
      email: 'testuser@example.com',
      password: 'Test@123',
    };

    // Login
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('button[type="submit"]').click();

    // Wait for login to complete
    cy.url().should('include', '/menu');

    // Refresh the page
    cy.reload();

    // Should still be logged in
    cy.get('button').contains('Logout').should('exist');
    cy.get('button').contains('Menu Management').should('exist');
  });
});
