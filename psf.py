# Base class for PSF

class PSF():

    def __init__(self, filter, config_file=None,
                 config_output_file=None, model_file=None):
        self.filter = filter
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.model_file = model_file

    def write_config(self, d):
        pass

    def edit_confit(self, d):
        assert self.config_file is not None

    def alter_config(self, d):
        assert self.config_file is not None

    def optimize_config(self):
        pass

    def visualize(self, d):
        assert self.config_output_file is not None
        d.set("mecube new " + self.config_output_file)

    def set_model(self):
        pass