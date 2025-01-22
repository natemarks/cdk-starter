- [ ] app_vpc stack
- [ ] public/private ECS stack
- [ ] public/private ASG stack
- [ ] app runner stack
- [ ] Add waf options
- [ ] api and cloudfront UI
- 
- [ ] fix tests.unit.rel1977_1.test_inventory.test_locations test to use test data instead of edit/ data. check results.
- [ ] automate the copy/create of a new release (make target?)
- [ ] how-to: add a  new release. (explain release naming rules: no underscores, etc.)
- [ ] how-to: add a new stack and test
- [ ] how-to: update settings/stack input
- [ ] reference: test organization
- [ ] how-to: add a release pipeline
- [ ] add dynatrace_activegate
- [ ] add tests for config.helper.underscore_to_pascal_case and config.helper.pascal_case_to_underscore
- [ ] get rid of RDS code


cleanup:

data/
docs/RELEASE.md


how to docs:




common tasks:

add new stack:
- add settings to edit/
- add stack module to release/stack
- add tests to test/stack
- add discovery logic to release/discover
- add stack to release/inventory