from commonconf import override_settings


fdao_spotseeker_override = override_settings(
    RESTCLIENTS_SPOTSEEKER_DAO_CLASS='Mock')
