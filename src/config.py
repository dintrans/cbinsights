import validators

parameters = {
    'CACHE_SLOTS': 10000,
    'OBJECT_TTL': 3600,
    'EVICTION_POLICY': "REJECT"
}
parameters_validator = {
    'CACHE_SLOTS': lambda x: validators.positive_int_validator(x),
    'OBJECT_TTL': lambda x: validators.positive_int_validator(x),
    'EVICTION_POLICY': lambda x: validators.str_in_array_validator(x, __ep_opt)
}
eviction_policy_translator = {
    'OLDEST_FIRST': 'FIFO',
    'NEWEST_FIRST': 'LIFO',
    'REJECT': 'Reject',
}

__ep_opt = ["OLDEST_FIRST", "NEWEST_FIRST", "REJECT"]
