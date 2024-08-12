# List of packages
packages <- c("httr", "httr2", "jsonlite", "scales", "methods", "knitr")

# Install packages if not already installed
new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)

# Load the packages and suppress the output
invisible(lapply(packages, function(pkg) {
  library(pkg, character.only = TRUE)
}))