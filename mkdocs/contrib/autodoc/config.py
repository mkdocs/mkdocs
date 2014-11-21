# reference to the base mkdocs configruation
base_config = {}

# ignore modules by the inputed name
# any module that is in this list will not be included for documentation generation
ignore = []

#--------------------------------

def update(options):
    """
    Updates the global settings for this configuration file from the inputed config options.
    """
    globals().update(options)