#
# Template for Spells
# Remember to place commas after each line!
#

SPELL_PANDACANNON =     {
                            'name':             'PandaCannon',
                            'modelPath':        'panda', 
                            'anims':            {},
                            'damage':           10,
                            'hitThreshold':     30,
                            'cooldown':         1.0, # in seconds, after chargeSequence is complete
                            'attackRange':      250, # to launch a projectile
                            'mass':             0.004,
                            'chargeSequence':   {
                                                    'firstAnimation':       'anim_chargeFemale',
                                                    'firstAnimationTime':   1.0,
                                                    'secondAnimation':      'anim_attackFemale',
                                                    'secondAnimationTime':  1.0,
                                                    'idleAnimation':        'anim_idleFemale'
                                                }
                        }

SPELL_NEEDLES =         {
                            'name':             'Needles',
                            'modelPath':        './LEGameAssets/Models/attack_light.egg', 
                            'anims':            {},  # key and egg file
                            'damage':           10,
                            'hitThreshold':     30,
                            'cooldown':         1.0, # in seconds, after chargeSequence is complete
                            'attackRange':      250, # to launch a projectile
                            'mass':             0.004,  # lower mass travels faster
                            'chargeSequence':   {
                                                    'firstAnimation':       'anim_chargeFemale',
                                                    'firstAnimationTime':   1.0,
                                                    'secondAnimation':      'anim_attackFemale',
                                                    'secondAnimationTime':  1.0,
                                                    'idleAnimation':        'anim_idleFemale'
                                                }
                        }

SPELL_SPOREBLAST =      {
                            'name':             'SporeBlast',
                            'modelPath':        './LEGameAssets/Models/attack_medium.egg', 
                            'anims':            {},
                            'damage':           15,
                            'hitThreshold':     30,
                            'cooldown':         1.0, # in seconds, after chargeSequence is complete
                            'attackRange':      250, # to launch a projectile
                            'mass':             0.004,
                            'chargeSequence':   {
                                                    'firstAnimation':       'anim_chargeFemale',
                                                    'firstAnimationTime':   1.0,
                                                    'secondAnimation':      'anim_attackFemale',
                                                    'secondAnimationTime':  1.0,
                                                    'idleAnimation':        'anim_idleFemale'
                                                }
                        }

SPELL_GUASSBOOM =       {
                            'name':             'GuassBoom',
                            'modelPath':        './LEGameAssets/Models/attack_heavy.egg', 
                            'anims':            {},
                            'damage':           20,
                            'hitThreshold':     30,
                            'cooldown':         1.0, # in seconds, after chargeSequence is complete
                            'attackRange':      250, # to launch a projectile
                            'mass':             0.004,
                            'chargeSequence':   {
                                                    'firstAnimation':       'anim_chargeFemale',
                                                    'firstAnimationTime':   1.0,
                                                    'secondAnimation':      'anim_attackFemale',
                                                    'secondAnimationTime':  1.0,
                                                    'idleAnimation':        'anim_idleFemale'
                                                }
                        }

SPELL_ENEMYBLAST =      {
                            'name':             'SporeBlast',
                            'modelPath':        './LEGameAssets/Models/attack_enemy.egg', 
                            'anims':            {},
                            'damage':           10,
                            'hitThreshold':     30,
                            'cooldown':         1.0, # in seconds, after chargeSequence is complete
                            'attackRange':      100, # to launch a projectile; note that enemies will by default stop getting closer to their target at 70
                            'mass':             0.004,
                            'chargeSequence':   {
                                                    'firstAnimation':       'anim_chargeMale',
                                                    'firstAnimationTime':   1.0,
                                                    'secondAnimation':      'anim_attackMale',
                                                    'secondAnimationTime':  1.0,
                                                    'idleAnimation':        'anim_idleMale'
                                                }
                        }

ATTACK_LIGHT = SPELL_NEEDLES
ATTACK_MEDIUM = SPELL_SPOREBLAST
ATTACK_HEAVY = SPELL_GUASSBOOM
ATTACK_ENEMY = SPELL_ENEMYBLAST