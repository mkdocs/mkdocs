all # Use all markdownlint rules

# Disable line length check for tables and code blocks
rule 'MD013', :line_length => 80, :code_blocks => false, :tables => false

# Set Ordered list item prefix to "ordered" (use 1. 2. 3. not 1. 1. 1.)
rule 'MD029', :style => "ordered"
