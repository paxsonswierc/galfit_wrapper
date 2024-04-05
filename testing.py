config = open('r_band_config.txt', 'r')
config = open('galfit.txt', 'r')
lines = config.readlines()

for i, line in enumerate(lines):
    if 'sersic' in line and 'sersic,' not in line:
        for component_line in lines[i+1:]:
            words = component_line.split()
            if '1)' in component_line:
                x = float(words[1])
                y = float(words[2])
            elif '4) ' in component_line and '=4)' not in component_line:
                a = float(words[1])
            elif '9)' in component_line:
                b_over_a = float(words[1])
                b = b_over_a * a
            elif '10)' in component_line:
                angle = float(words[1])
                if angle >= 270:
                    angle -= 90
                else:
                    angle += 90
            elif '0)' in component_line:
                break
    if '0) psf' in component_line:
        for component_line in lines[i+1:]:
            words = component_line.split()
            if '1)' in component_line:
                x = float(words[1])
                y = float(words[2])
            elif '0)' in component_line:
                break
            