def config_to_constraint(self):
    if self.config_file is None:
            print('Please create or upload galfit config file first')
    else:
        config = open(self.config_file, 'r')
        lines = config.readlines()
        
        constraint_lines = []
        comp_num = 0
        comp_type = ""
        for i, line in enumerate(lines):
            # check for a line that contains the start of a component
            if 'Component number:' in line:
                comp_num += 1
            words = line.split()
            # gets the component type (psft, sersic, sky, etc.)
            if '0)' in line and '=0)' not in line and '10)' not in line:
                comp_type = words[1]
            # excludes sky component type in constraints (and other unsupported types)
            if comp_type == 'psf' or comp_type == 'sersic' or comp_type == 'moffat':
                # constraints the x and y to +/- 1 pixels
                if '1)' in line:
                    constraint_lines.append(f"{comp_num} x -1 1")
                    constraint_lines.append(f"{comp_num} y -1 1")
                # constraints the magnitude to +/- 4 apparent magnitudes
                elif '3) ' in line:
                    constraint_lines.append(f"{comp_num} 3 -4 4")
                # excludes psf component type, since other constraints don't apply
                if comp_type == 'sersic' or comp_type == 'moffat':
                    # constraints the FWHM by +/- 10% of value
                    if '4) ' in line:
                        a = float(words[1])
                        constraint_lines.append(f"{comp_num} 4 -{0.1*a:.5f} {0.1*a:.5f}")
                    # constraints the sersic index/moffat powerlaw to +/- 10% of value
                    if '5) ' in line:
                        index = float(words[1])
                        constraint_lines.append(f"{comp_num} 5 -{0.1*index:.5f} {0.1*index:.5f}")
                    # constraints the axis ratio to +/- 10% of value
                    elif '9) ' in line:
                        b_over_a = float(words[1])
                        constraint_lines.append(f"{comp_num} 9 -{0.1*b_over_a:.5f} {0.1*b_over_a:.5f}")
                    # constraints the rotation to +/- 5 degrees
                    elif '10) ' in line:
                        constraint_lines.append(f"{comp_num} 10 -5 5")
        
        config.close()

        # creates a text file from list of constraints     
        constraint_contents = "\n".join(constraint_lines)
        self.constraint_file = self.ouput_dir + self.target_filename + '_constraint.txt'
        with open(self.constraint_file, 'w') as h:
            h.write("\n".join(constraint_lines))