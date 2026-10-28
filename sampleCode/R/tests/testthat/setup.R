# Points the samples' logs, token cache, and reports at a temporary folder for the
# whole run, so the tests never write into this sample's own folders.
test_root <- withr::local_tempdir(.local_envir = testthat::teardown_env())
withr::local_options(
  implan.sample_root = test_root,
  .local_envir = testthat::teardown_env()
)
