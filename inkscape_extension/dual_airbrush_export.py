#!/usr/bin/env python3
import inkex
from lxml import etree

class DualAirbrushExport(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--black_layer", type=str, default="black")
        pars.add_argument("--white_layer", type=str, default="white")
        pars.add_argument("--z_height", type=float, default=2.0)
        pars.add_argument("--feedrate", type=int, default=1500)
        pars.add_argument("--output_path", type=str, default="dual_airbrush_output.gcode")

    def effect(self):
        gcode_lines = [
            "; Begin G-code for Dual Airbrush Plotter",
            "G90",
            "G21",
            "M451",
            "G28"
        ]
        for layer in self.svg.xpath('//svg:g', namespaces=inkex.NSS):
            label = layer.attrib.get(inkex.addNS('label', 'inkscape'))
            if label == self.options.black_layer:
                gcode_lines.append("; -- Black Brush Layer --")
                gcode_lines.append("G0 Z{:.2f}".format(self.options.z_height))
                gcode_lines.append("M42 P0 S1")
                gcode_lines.append("M280 P0 S90")
                gcode_lines.append("; Insert drawing commands for black layer here")
                gcode_lines.append("M280 P0 S0")
                gcode_lines.append("M42 P0 S0")
            elif label == self.options.white_layer:
                gcode_lines.append("; -- White Brush Layer --")
                gcode_lines.append("G0 Z{:.2f}".format(self.options.z_height))
                gcode_lines.append("M42 P1 S1")
                gcode_lines.append("M280 P1 S90")
                gcode_lines.append("; Insert drawing commands for white layer here")
                gcode_lines.append("M280 P1 S0")
                gcode_lines.append("M42 P1 S0")
        gcode_lines.append("M5 ; All air off")
        with open(self.options.output_path, "w") as f:
            f.write("\n".join(gcode_lines))

if __name__ == '__main__':
    DualAirbrushExport().run()
