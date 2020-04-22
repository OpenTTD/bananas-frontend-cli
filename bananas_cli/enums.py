from enum import Enum


class License(Enum):
    GPL_v2 = "GPL v2"
    GPL_v3 = "GPL v3"
    LGPL_v2_1 = "LGPL v2.1"
    CC_0_v1_0 = "CC-0 v1.0"
    CC_BY_v3_0 = "CC-BY v3.0"
    CC_BY_SA_v3_0 = "CC-BY-SA v3.0"
    CC_BY_NC_SA_v3_0 = "CC-BY-NC-SA v3.0"
    CC_BY_NC_ND_v3_0 = "CC-BY-NC-ND v3.0"
    CUSTOM = "Custom"
