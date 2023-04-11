import gym

env = gym.make('CartPole-v1')
state = env.reset()
for t in range(100):
    env.render()
    print(state)
    action = env.action_space.sample()
    state, reward, done, _, info = env.step(action)
    if done:
        print('Finished')
        break
env.close()