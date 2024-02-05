# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import override_settings


fdao_spotseeker_override = override_settings(
    RESTCLIENTS_SPOTSEEKER_DAO_CLASS='Mock')
