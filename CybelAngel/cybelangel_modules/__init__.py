from sekoia_automation.module import Module

from cybelangel_modules.models import CybelangelModuleConfiguration


class CybelangelModule(Module):
    configuration: CybelangelModuleConfiguration
