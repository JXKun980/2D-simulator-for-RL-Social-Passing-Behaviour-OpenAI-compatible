from gym.envs.registration import register

register(
    id='SocialNav-v0',
    entry_point='social_nav_env.envs:SocialNav',
)
