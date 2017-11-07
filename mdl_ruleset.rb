all # Use all markdownlint rules

# Disable line length check for tables and code blocks
rule 'MD013', :line_length => 80, :code_blocks => false, :tables => false
