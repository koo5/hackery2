/// <reference types="cypress" />

// Welcome to Cypress!
//
// This spec file contains a variety of sample tests
// for a todo list app that are designed to demonstrate
// the power of writing tests in Cypress.
//
// To learn more about how Cypress works and
// what makes it such an awesome testing tool,
// please read our getting started guide:
// https://on.cypress.io/introduction-to-cypress

describe('example to-do app', () => {
  beforeEach(() => {
    // Cypress starts out with a blank slate for each test
    // so we must tell it to visit our website with the `cy.visit()` command.
    // Since we want to visit the same URL at the start of all our tests,
    // we include it in our beforeEach function so that it runs before each test
    cy.visit('https://www.ato.gov.au/Calculators-and-tools/Host/?anchor=DIV7A#DIV7A/questions')
  })

  it('displays two todo items by default', () => {
    // We use the `cy.get()` command to get all elements that match the selector.
    // Then, we use `should` to assert that there are two matched items,
    // which are the two default items.
    cy.contains('Calculate a minimum yearly repayment and the amount of the loan not repaid by the end of an income year').click()


    let incomeYearOfLoan = [];
    cy.get('[id=ddl-incomeYearOfLoan]').find('option').each(($el) => {

      let t = $el[0].innerText;
      if (t != " - Select -")
      {
          console.log(t);
          incomeYearOfLoan.push(t)
      }
    })
    cy.writeFile('incomeYearOfLoan.json', incomeYearOfLoan)

    incomeYearOfLoan.+





  })
})
