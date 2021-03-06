import tensorflow as tf
import tensorlayer as tl
from tensorlayer.layers import *
from gym_torcs import TorcsEnv
import numpy as np
import time
import matplotlib.pyplot as plt

img_dim = [64, 64, 3]
n_action = 1        # steer only (float, left and right 1 ~ -1)
steps = 1000        # maximum step for a game
batch_size = 32
n_epoch = 100

def img_reshape(input_img):
    """ (3, 64, 64) --> (64, 64, 3) """
    _img = np.transpose(input_img, (1, 2, 0))
    _img = np.flipud(_img)
    _img = np.reshape(_img, (1, img_dim[0], img_dim[1], img_dim[2]))
    return _img

###================= Define model
class Agent(object):
    def __init__(self, name='model', sess=None):
        assert sess != None
        self.name = name
        self.sess = sess

        self.x = tf.placeholder(tf.float32, [None, img_dim[0], img_dim[1], img_dim[2]], name='Observaion')
        self.y = tf.placeholder(tf.float32, [None, n_action], name='Steer')

        self._build_net(True, False)
        self._build_net(False, True)
        self._define_train_ops()

        tl.layers.initialize_global_variables(self.sess)

        print()
        self.n_test.print_layers()
        print()
        self.n_test.print_params(False)
        print()
        # exit()

    def _build_net(self, is_train=True, reuse=None):
        with tf.variable_scope(self.name, reuse=reuse) as vs:
            tl.layers.set_name_reuse(reuse)

            n = InputLayer(self.x / 255, name='in')

            n = Conv2d(n, 32, (3, 3), (1, 1), tf.nn.relu, "VALID", name='c1/1')
            n = Conv2d(n, 32, (3, 3), (1, 1), tf.nn.relu, "VALID", name='c1/2')
            n = MaxPool2d(n, (2, 2), (2, 2), 'VALID', name='max1')

            n = DropoutLayer(n, 0.75, is_fix=True, is_train=is_train, name='drop1')

            n = Conv2d(n, 64, (3, 3), (1, 1), tf.nn.relu, "VALID", name='c2/1')
            n = Conv2d(n, 64, (3, 3), (1, 1), tf.nn.relu, "VALID", name='c2/2')
            n = MaxPool2d(n, (2, 2), (2, 2), 'VALID', name='max2')
            # print(n.outputs)
            n = DropoutLayer(n, 0.75, is_fix=True, is_train=is_train, name='drop2')

            n = FlattenLayer(n, name='f')
            n = DenseLayer(n, 512, tf.nn.relu, name='dense1')
            n = DropoutLayer(n, 0.5, is_fix=True, is_train=is_train, name='drop3')
            n = DenseLayer(n, n_action, tf.nn.tanh, name='o')

        if is_train:
            self.n_train = n
        else:
            self.n_test = n

    def _define_train_ops(self):
        self.cost = tl.cost.mean_squared_error(self.n_train.outputs, self.y, is_mean=False)
        self.train_params = tl.layers.get_variables_with_name(self.name, train_only=True, printable=False)
        self.train_op = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(self.cost, var_list=self.train_params)

    def train(self, X, y, n_epoch=100, batch_size=10, print_freq=20):
        for epoch in range(n_epoch):
            start_time = time.time()
            total_err, n_iter = 0, 0
            for X_, y_ in tl.iterate.minibatches(X, y, batch_size, shuffle=True):
                _, err = self.sess.run([self.train_op, self.cost], feed_dict={self.x: X_, self.y: y_})
                total_err += err
                n_iter += 1
            if epoch % print_freq == 0:
                print("Epoch [%d/%d] cost:%f took:%fs" % (epoch, n_epoch, total_err/n_iter, time.time()-start_time))

    def predict(self, image):
        a = self.sess.run(self.n_test.outputs, {self.x : image})
        return a

    def save_model(self):
        tl.files.save_npz(self.n_test.all_params, name=self.name+'.npz', sess=self.sess)

    def load_model(self):
        tl.files.load_and_assign_npz(sess=self.sess, name=self.name+'.npz', network=self.n_test)

###===================== Pretrain model using data for demonstration
sess = tf.InteractiveSession()
model = Agent(name='model', sess=sess)
model.load_model()

act_list=[]
ob_list = []

env = TorcsEnv(vision=True, throttle=False)
ob = env.reset(relaunch=True)
reward_sum = 0.0
for i in range(1000):
    act = model.predict(img_reshape(ob.img))
    #print(act)#[[0.10428748]]
    act_list.append(act[0][0])
    ob, reward, done, _ = env.step(act)
    if done is True:
         break
    else:
         ob_list.append(ob)
    reward_sum += reward
print("# step: %d reward: %f " % (i, reward_sum))
print("PLAY WITH THE TRAINED MODEL\n")
env.end()


aa =  [[ 0.00000000e+00],
       [ 2.01715099e-06],
       [-4.43620848e-04],
       [-2.99355684e-03],
       [-4.63886547e-03],
       [-4.49163778e-03],
       [-4.13948182e-03],
       [-3.62492433e-03],
       [-2.92368139e-03],
       [-1.95681841e-03],
       [-1.29047801e-03],
       [-9.71716221e-04],
       [-6.92427930e-04],
       [-2.59829838e-04],
       [-2.82578201e-04],
       [-2.67380837e-04],
       [-2.71905663e-04],
       [-2.77958031e-04],
       [-2.15708090e-04],
       [-1.48895524e-04],
       [-2.59677250e-04],
       [-2.55028470e-04],
       [-2.18572161e-04],
       [-2.97470066e-04],
       [-2.95933288e-04],
       [-2.27593180e-04],
       [-2.41225156e-04],
       [-3.03427066e-04],
       [-3.20095099e-04],
       [-3.24608768e-04],
       [-3.27607302e-04],
       [-3.18471842e-04],
       [-3.22985533e-04],
       [-3.26069899e-04],
       [-3.22995070e-04],
       [-3.19923438e-04],
       [-3.22909239e-04],
       [-3.25907774e-04],
       [-3.22823409e-04],
       [-3.22785262e-04],
       [-3.22737578e-04],
       [-3.22689895e-04],
       [-3.22575453e-04],
       [-3.22527770e-04],
       [-3.22480086e-04],
       [-3.22432402e-04],
       [-3.22384718e-04],
       [-3.22327498e-04],
       [-3.22279814e-04],
       [-3.22222594e-04],
       [-3.22251204e-04],
       [-3.22203520e-04],
       [-3.22146300e-04],
       [-3.22089079e-04],
       [-3.22031859e-04],
       [-3.21965102e-04],
       [-3.21907881e-04],
       [-3.21783904e-04],
       [-3.21717148e-04],
       [-3.21659928e-04],
       [-3.21593168e-04],
       [-3.24572630e-04],
       [-3.29060881e-04],
       [-2.36044195e-04],
       [-2.39332326e-04],
       [-2.42607742e-04],
       [-3.96564688e-04],
       [-8.35759062e-04],
       [-4.34150693e-04],
       [-1.34280527e-03],
       [-9.33528742e-04],
       [-9.38947143e-05],
       [-1.62302800e-05],
       [-1.55831581e-05],
       [-1.57897403e-05],
       [-1.59845456e-05],
       [-1.61783956e-05],
       [-8.51962277e-03],
       [-2.24068409e-01],
       [-2.18061523e-01],
       [-1.80155487e-01],
       [-1.84189094e-01],
       [-1.87327572e-01],
       [-1.86063703e-01],
       [-1.84954572e-01],
       [-1.84490391e-01],
       [-1.84688903e-01],
       [-9.37968502e-02],
       [ 4.07625884e-02],
       [ 6.95723749e-03],
       [-5.08629545e-03],
       [ 2.29609414e-04],
       [ 1.10111685e-03],
       [ 3.63217182e-04],
       [ 7.48632930e-05],
       [-4.15586344e-04],
       [-1.20486496e-03],
       [-1.08596145e-03],
       [-1.12310287e-03],
       [-1.40364843e-03],
       [-1.91286059e-03],
       [-9.35749648e-04],
       [-6.08474832e-04],
       [-1.23136245e-05],
       [-1.74866751e-04],
       [-1.13273393e-04],
       [ 9.54152486e-05],
       [ 3.60235516e-04],
       [ 5.88868364e-04],
       [-2.77032281e-04],
       [-1.55353252e-04],
       [ 6.16010960e-05],
       [ 2.83588910e-04],
       [ 5.03252536e-04],
       [-4.03910861e-04],
       [-2.93542845e-04],
       [-9.35262767e-05],
       [ 1.12510176e-04],
       [ 3.15384228e-04],
       [ 5.22048101e-04],
       [-5.66595665e-04],
       [ 2.60004035e-04],
       [-1.28942986e-04],
       [-3.26730213e-04],
       [-2.01579350e-04],
       [-2.54704553e-05],
       [ 1.26433676e-04],
       [ 3.01280161e-04],
       [ 4.78410099e-04],
       [ 6.50126938e-04],
       [-3.07893274e-04],
       [-2.58137827e-04],
       [-8.91804941e-05],
       [ 5.48569056e-05],
       [ 2.83445358e-04],
       [ 7.81435858e-04],
       [-1.86113123e-04],
       [-1.10722223e-04],
       [ 2.37682075e-05],
       [ 1.61952469e-04],
       [ 1.16783258e-01],
       [ 2.17293365e-01],
       [ 1.95542449e-01],
       [ 1.81879823e-01],
       [ 1.84550735e-01],
       [ 1.84166002e-01],
       [ 1.83551934e-01],
       [ 1.81882219e-01],
       [ 1.81402474e-01],
       [ 1.81293528e-01],
       [ 1.80331856e-01],
       [ 1.79597991e-01],
       [ 1.78279411e-01],
       [ 1.78322872e-01],
       [ 1.77972101e-01],
       [ 1.77123654e-01],
       [ 1.76783148e-01],
       [ 1.76173677e-01],
       [ 1.76781713e-01],
       [ 1.76864503e-01],
       [ 1.77130871e-01],
       [ 1.77616776e-01],
       [ 1.77384853e-01],
       [ 1.78111245e-01],
       [ 1.78193418e-01],
       [ 1.78377545e-01],
       [ 1.78649910e-01],
       [ 1.78246597e-01],
       [ 1.78709208e-01],
       [ 1.78468833e-01],
       [ 1.79043733e-01],
       [ 1.78983536e-01],
       [ 1.79239259e-01],
       [ 6.19311264e-02],
       [-3.52903591e-03],
       [-6.27981546e-03],
       [-3.32175911e-03],
       [-3.18834158e-03],
       [-2.99979188e-03],
       [-2.23949002e-03],
       [-1.43381349e-03],
       [-1.32804254e-03],
       [ 8.28098720e-02],
       [ 8.94729263e-02],
       [ 8.22100525e-02],
       [ 8.00008942e-02],
       [ 8.16452604e-02],
       [ 8.09520014e-02],
       [ 8.02197559e-02],
       [ 8.00427031e-02],
       [ 7.96757989e-02],
       [ 8.15869479e-02],
       [ 8.06046685e-02],
       [ 8.09347638e-02],
       [ 8.05348050e-02],
       [ 8.26517587e-02],
       [ 8.15068958e-02],
       [ 8.13966642e-02],
       [ 8.14941781e-02],
       [ 8.33475982e-02],
       [ 8.21815256e-02],
       [ 8.20080630e-02],
       [ 8.15358353e-02],
       [ 8.16302305e-02],
       [ 8.15290567e-02],
       [ 8.13662686e-02],
       [ 8.22041754e-02],
       [ 8.21181977e-02],
       [ 8.19431277e-02],
       [ 8.17553268e-02],
       [ 8.15574513e-02],
       [ 8.18521245e-02],
       [ 8.11780450e-02],
       [ 8.19993337e-02],
       [ 8.18417490e-02],
       [ 8.24769105e-02],
       [ 8.16873532e-02],
       [ 8.13354973e-02],
       [ 8.20634554e-02],
       [ 8.18831127e-02],
       [ 8.33658438e-02],
       [ 8.05001608e-02],
       [ 8.12162174e-02],
       [ 8.19743909e-02],
       [ 8.48262693e-02],
       [ 7.82883333e-02],
       [ 8.20417597e-02],
       [ 8.19916472e-02],
       [ 8.59219963e-02],
       [ 7.56558319e-02],
       [ 8.01183416e-02],
       [ 8.08130302e-02],
       [ 8.06623493e-02],
       [-1.45375769e-01],
       [-1.87875354e-01],
       [-1.56213132e-01],
       [-1.50964314e-01],
       [-1.55480716e-01],
       [-1.54697929e-01],
       [-1.55172729e-01],
       [-1.54040662e-01],
       [-1.54519343e-01],
       [-1.53142857e-01],
       [-1.53489828e-01],
       [-1.54148607e-01],
       [-1.52370957e-01],
       [-1.53838168e-01],
       [-1.51045017e-01],
       [-1.52803580e-01],
       [-1.51558297e-01],
       [-1.49884744e-01],
       [-1.48710589e-01],
       [ 3.84417518e-02],
       [ 1.91927005e-02],
       [-6.55195003e-03],
       [-8.15694487e-04],
       [ 9.22210684e-04],
       [-2.14247586e-04],
       [-6.87069130e-04],
       [-1.95665092e-04],
       [-1.05740637e-03],
       [-1.13482889e-03],
       [-1.36970965e-03],
       [-1.84286751e-03],
       [-1.40651646e-03],
       [-1.66759407e-03],
       [-5.64872724e-04],
       [-1.26604476e-04],
       [-5.23893442e-04],
       [ 5.81081144e-04],
       [-3.25446892e-04],
       [-3.91095007e-04],
       [-3.87290770e-04],
       [-3.85011632e-04],
       [-3.81978216e-04],
       [-3.80080941e-04],
       [-3.77413217e-04],
       [-3.77433147e-04],
       [-3.77433147e-04],
       [-3.80838554e-04],
       [-3.83114542e-04],
       [-3.87669484e-04],
       [-3.92221276e-04],
       [-3.94510473e-04],
       [-5.03792573e-04],
       [ 2.20977188e-04],
       [-3.51999792e-04],
       [-7.28799117e-04],
       [ 3.67447542e-04],
       [ 4.48279466e-04],
       [ 4.51296102e-04],
       [ 4.52053715e-04],
       [ 4.51685059e-04],
       [ 4.51306160e-04],
       [ 4.50927446e-04],
       [ 4.50548547e-04],
       [ 5.20735432e-04],
       [-2.44624839e-04],
       [-3.45550725e-04],
       [-3.51620893e-04],
       [-3.51242179e-04],
       [-3.50481416e-04],
       [-3.50850258e-04],
       [ 1.34644145e-01],
       [ 1.67556098e-01],
       [ 1.44643934e-01],
       [ 1.44335979e-01],
       [ 1.45648660e-01],
       [ 1.43597466e-01],
       [ 1.44229217e-01],
       [ 1.43577589e-01],
       [ 1.42109658e-01],
       [ 1.42943807e-01],
       [ 1.42041581e-01],
       [ 1.41589371e-01],
       [ 1.40997237e-01],
       [ 1.41799152e-01],
       [ 1.42053609e-01],
       [ 1.42587703e-01],
       [ 1.42524131e-01],
       [ 1.42672046e-01],
       [ 1.43105221e-01],
       [ 1.43777356e-01],
       [ 1.43654128e-01],
       [ 1.43764744e-01],
       [ 1.44251529e-01],
       [ 1.44647740e-01],
       [ 1.44416465e-01],
       [ 1.45248101e-01],
       [ 1.45815218e-01],
       [ 1.44923368e-01],
       [ 1.45468363e-01],
       [ 1.46295118e-01],
       [ 1.46635510e-01],
       [ 1.44812726e-01],
       [ 1.45249598e-01],
       [ 1.27563382e-01],
       [-8.67987137e-03],
       [-1.29959510e-02],
       [-6.99494262e-04],
       [ 1.62569635e-04],
       [-4.18573093e-04],
       [-9.04164841e-04],
       [-2.95339798e-04],
       [-6.48899024e-04],
       [ 7.12609260e-05],
       [-2.29735116e-04],
       [-4.48828681e-04],
       [-9.30299485e-04],
       [ 8.00113395e-05],
       [-3.13547995e-04],
       [-1.57888773e-04],
       [ 2.32468897e-04],
       [-2.52257974e-04],
       [-6.15478683e-04],
       [ 1.17206527e-04],
       [-1.74649979e-04],
       [-2.78323507e-04],
       [-4.04490315e-05],
       [ 5.02492397e-04],
       [ 1.96142155e-04],
       [ 1.23323398e-03],
       [ 1.42992534e-03],
       [ 1.81538607e-03],
       [ 1.17477541e-03],
       [-1.62089720e-01],
       [-1.68854851e-01],
       [-1.45734648e-01],
       [-1.48101205e-01],
       [-1.49671472e-01],
       [-1.48747053e-01],
       [-1.50063969e-01],
       [-1.49858608e-01],
       [-1.49367130e-01],
       [-1.51038276e-01],
       [-1.50318262e-01],
       [-1.50287740e-01],
       [-1.51324217e-01],
       [-1.50593989e-01],
       [-1.49277767e-01],
       [-1.50347039e-01],
       [-1.49819911e-01],
       [-1.49161358e-01],
       [-1.49258575e-01],
       [-1.48999720e-01],
       [-1.48736383e-01],
       [-1.48010242e-01],
       [-1.48146320e-01],
       [-1.48118420e-01],
       [-1.47849381e-01],
       [-1.47299568e-01],
       [-1.47520487e-01],
       [-1.46823461e-01],
       [-1.46204919e-01],
       [-1.47010423e-01],
       [-1.46947086e-01],
       [-1.45445917e-01],
       [-1.47125854e-01],
       [-1.45418457e-01],
       [-1.46071496e-01],
       [-1.46561232e-01],
       [-1.43260416e-01],
       [-1.46172619e-01],
       [-1.44710086e-01],
       [-1.44097976e-01],
       [-1.46330828e-01],
       [-1.42560261e-01],
       [-1.42234263e-01],
       [ 2.24349587e-02],
       [ 1.89545100e-02],
       [-6.37264753e-03],
       [-2.03425584e-04],
       [ 1.64854211e-03],
       [ 4.89883228e-04],
       [ 1.85791830e-03],
       [ 1.26580025e-03],
       [ 1.89106013e-03],
       [ 1.66471937e-03],
       [ 1.51939725e-03],
       [ 1.58215854e-03],
       [ 1.23356564e-03],
       [ 1.58623075e-03],
       [ 5.62533731e-04],
       [-3.77148505e-04],
       [-3.34361803e-05],
       [ 4.37189020e-04],
       [ 9.01558581e-04],
       [ 2.77700174e-04],
       [ 6.52285337e-04],
       [ 4.59978786e-05],
       [ 4.00584104e-04],
       [ 8.38239503e-04],
       [ 2.06062801e-04],
       [ 5.54285558e-04],
       [-1.15508175e-04],
       [ 2.17904745e-04],
       [ 6.50241427e-04],
       [-6.14532066e-05],
       [ 2.53993669e-04],
       [ 6.70116382e-04],
       [-5.57744820e-05],
       [ 2.28347592e-04],
       [ 7.90862451e-04],
       [ 4.78911698e-04],
       [ 1.51338516e-03],
       [ 6.27076330e-04],
       [ 9.36455518e-04],
       [ 1.02917499e-03],
       [ 7.81769367e-04],
       [ 1.93310644e-04],
       [ 4.24886709e-04],
       [ 7.20595308e-04],
       [-5.91895359e-05],
       [ 1.61493298e-04],
       [ 4.64154141e-04],
       [ 7.73911423e-04],
       [-4.30380627e-05],
       [ 1.51564260e-04],
       [ 4.53296244e-04],
       [ 7.52667966e-04],
       [-1.23239699e-04],
       [ 5.15493027e-05],
       [ 1.41417999e-04],
       [-5.39707915e-05],
       [ 3.20059626e-03],
       [ 3.54259506e-02],
       [ 3.05845501e-02],
       [ 2.72057966e-02],
       [ 2.69850109e-02],
       [ 2.80532859e-02],
       [ 2.76795927e-02],
       [ 2.79580128e-02],
       [ 2.87901637e-02],
       [ 2.83884911e-02],
       [ 2.96001065e-02],
       [ 2.90831157e-02],
       [ 2.95453550e-02],
       [ 2.93821413e-02],
       [ 3.04307068e-02],
       [ 3.01644726e-02],
       [ 2.94169264e-02],
       [ 2.94242824e-02],
       [ 2.91776757e-02],
       [ 2.86153790e-02],
       [ 2.76777006e-02],
       [ 2.77190160e-02],
       [ 2.73848728e-02],
       [ 2.80488002e-02],
       [ 2.77144534e-02],
       [ 2.70669080e-02],
       [ 2.81447304e-02],
       [ 2.87565914e-02],
       [ 2.78691717e-02],
       [ 2.89127454e-02],
       [ 2.86345517e-02],
       [ 2.86593809e-02],
       [ 2.89731944e-02],
       [ 2.96438053e-02],
       [ 2.94100651e-02],
       [ 3.01623172e-02],
       [ 3.03200971e-02],
       [ 3.13232338e-02],
       [ 3.03610310e-02],
       [ 2.94861131e-02],
       [ 3.08459618e-02],
       [ 2.89367376e-02],
       [ 2.84243256e-02],
       [ 2.98073693e-02],
       [ 2.81884261e-02],
       [ 2.82258953e-02],
       [ 2.85831965e-02],
       [ 2.72872192e-02],
       [ 2.79719538e-02],
       [ 2.74598221e-02],
       [ 2.77773994e-02],
       [ 2.70336776e-02],
       [ 2.72401022e-02],
       [ 2.80447490e-02],
       [ 2.82323288e-02],
       [ 2.82760588e-02],
       [ 2.86291770e-02],
       [ 2.82290585e-02],
       [ 2.95158458e-02],
       [ 2.81105719e-02],
       [ 2.94205984e-02],
       [ 3.05774696e-02],
       [ 2.84923781e-02],
       [ 3.05510182e-02],
       [ 3.01692522e-02],
       [ 8.55903726e-02],
       [ 8.71973245e-02],
       [ 8.16372161e-02],
       [ 8.10254121e-02],
       [ 8.14117877e-02],
       [ 8.20077975e-02],
       [ 8.08305424e-02],
       [ 8.03356172e-02],
       [ 8.04223059e-02],
       [ 8.09208777e-02],
       [ 7.96392796e-02],
       [ 7.97085182e-02],
       [ 8.01310414e-02],
       [ 8.09289501e-02],
       [ 8.11214364e-02],
       [ 8.14205157e-02],
       [ 8.20194363e-02],
       [ 8.17901207e-02],
       [ 8.19306212e-02],
       [ 8.22778558e-02],
       [ 8.28895355e-02],
       [ 8.27925882e-02],
       [ 8.25079901e-02],
       [ 8.24043786e-02],
       [ 8.31861301e-02],
       [ 8.30498833e-02],
       [ 8.28181251e-02],
       [ 8.25596063e-02],
       [ 8.22871510e-02],
       [ 8.30198201e-02],
       [ 8.28030622e-02],
       [ 8.24839137e-02],
       [ 8.33855356e-02],
       [ 8.29504578e-02],
       [ 8.22845437e-02],
       [ 8.22776645e-02],
       [ 8.24559220e-02],
       [ 8.14113297e-02],
       [ 8.21030844e-02],
       [ 8.21570533e-02],
       [ 8.24700716e-02],
       [ 8.34360849e-02],
       [ 8.10516463e-02],
       [ 8.13810311e-02],
       [ 8.13865633e-02],
       [ 8.20948348e-02],
       [ 8.22094297e-02],
       [ 8.12708935e-02],
       [ 8.18754966e-02],
       [ 8.10963149e-02],
       [ 8.28713176e-02],
       [ 7.79730812e-02],
       [ 8.02859421e-02],
       [ 8.03111451e-02],
       [ 8.05060320e-02],
       [ 6.67728317e-02],
       [ 4.34729211e-02],
       [ 4.82921281e-02],
       [ 5.01191589e-02],
       [ 5.05202983e-02],
       [ 4.86528403e-02],
       [ 4.89727443e-02],
       [ 4.91739332e-02],
       [ 4.89808322e-02],
       [ 4.92406823e-02],
       [ 4.73247779e-02],
       [ 4.82570178e-02],
       [ 4.77728759e-02],
       [ 4.73535949e-02],
       [ 4.64353717e-02],
       [ 4.71691656e-02],
       [ 4.64265567e-02],
       [ 4.65227832e-02],
       [ 4.49658897e-02],
       [ 4.60284061e-02],
       [ 4.66351473e-02],
       [ 4.64763745e-02],
       [ 4.76840770e-02],
       [ 4.71857416e-02],
       [ 4.79400945e-02],
       [ 4.80928858e-02],
       [ 4.83146126e-02],
       [ 4.91459441e-02],
       [ 4.84720589e-02],
       [ 4.83596184e-02],
       [ 4.79595651e-02],
       [ 4.66691959e-02],
       [ 4.71614237e-02],
       [ 4.67089983e-02],
       [ 4.67013647e-02],
       [ 4.64774533e-02],
       [ 4.90057062e-02],
       [ 4.80023159e-02],
       [ 4.82464191e-02],
       [ 4.89521181e-02],
       [ 4.72946450e-02],
       [ 4.92509128e-02],
       [ 4.77318241e-02],
       [ 4.75752218e-02],
       [ 4.72924065e-02],
       [ 4.97002453e-02],
       [ 4.78666528e-02],
       [ 4.76644827e-02],
       [ 4.79669979e-02],
       [ 4.86425103e-02],
       [ 4.86009366e-02],
       [ 4.81496627e-02],
       [ 4.83794886e-02],
       [ 4.83335335e-02],
       [ 4.79228849e-02],
       [ 4.78406645e-02],
       [ 4.81445169e-02],
       [ 4.88136263e-02],
       [ 4.87732560e-02],
       [ 4.83164079e-02],
       [ 4.85678756e-02],
       [ 4.74460365e-02],
       [ 4.87026429e-02],
       [ 4.83635032e-02],
       [ 4.92826886e-02],
       [ 4.88988497e-02],
       [ 4.80474682e-02],
       [ 4.78790142e-02],
       [ 4.74333531e-02],
       [ 4.83944654e-02],
       [ 4.87688167e-02],
       [ 4.83509731e-02],
       [ 4.92634589e-02],
       [ 4.88765002e-02],
       [ 4.80086806e-02],
       [ 4.78457411e-02],
       [ 4.80879094e-02],
       [ 4.87011834e-02],
       [ 4.79309673e-02],
       [ 4.84433490e-02],
       [ 4.87428910e-02],
       [ 4.75878233e-02],
       [ 4.77264252e-02],
       [ 4.83262725e-02],
       [ 4.93021942e-02],
       [ 4.88883467e-02],
       [ 4.80004295e-02],
       [ 4.77839300e-02],
       [ 4.72946305e-02],
       [ 3.48434582e-02],
       [-1.02321093e-01],
       [-9.81219899e-02],
       [-8.19609299e-02],
       [-8.30933334e-02],
       [-8.45285292e-02],
       [-8.44560662e-02],
       [-8.60498809e-02],
       [-8.44427796e-02],
       [-8.53626048e-02],
       [-8.55716261e-02],
       [-8.35206562e-02],
       [-8.40575243e-02],
       [-8.49055739e-02],
       [-8.39308253e-02],
       [-8.42033600e-02],
       [-8.41423226e-02],
       [-8.31462853e-02],
       [-8.28928531e-02],
       [-8.21040797e-02],
       [-8.19090926e-02],
       [-8.12100193e-02],
       [-8.09537402e-02],
       [-8.06192500e-02],
       [-7.94636521e-02],
       [-7.99259143e-02],
       [-8.05555689e-02],
       [-7.99270427e-02],
       [-8.05235580e-02],
       [-8.13214046e-02],
       [-8.19736408e-02],
       [-8.15644039e-02],
       [-8.20410584e-02],
       [-8.27874526e-02],
       [-8.24497734e-02],
       [-8.36345656e-02],
       [-8.25655917e-02],
       [-8.15207402e-02],
       [-8.65812632e-03],
       [ 1.29564792e-02],
       [-9.84205214e-04],
       [-1.80492711e-03],
       [-2.99284569e-05],
       [-8.81608215e-04],
       [-1.02743831e-03],
       [-1.36458275e-03],
       [-1.96776182e-03],
       [-1.66873809e-03],
       [-1.47420355e-03],
       [-2.67232862e-03],
       [-1.87287077e-03],
       [-1.66270170e-03],
       [-1.17897350e-03],
       [-1.42607975e-03],
       [-1.41256659e-03],
       [ 3.11989281e-02],
       [ 9.09615367e-02],
       [ 8.53318245e-02],
       [ 8.02262867e-02],
       [ 8.05971173e-02],
       [ 8.09618642e-02],
       [ 8.16271396e-02],
       [ 8.14835982e-02],
       [ 8.25479825e-02],
       [ 8.20237329e-02],
       [ 8.27691345e-02],
       [ 8.26071326e-02],
       [ 8.28064829e-02],
       [ 8.27307980e-02],
       [ 8.19492218e-02],
       [ 8.19145725e-02],
       [ 8.15715712e-02],
       [ 8.06365164e-02],
       [ 8.04014677e-02],
       [ 8.09114438e-02],
       [ 8.00436847e-02],
       [ 7.97113134e-02],
       [ 7.91381874e-02],
       [ 7.99322710e-02],
       [ 8.01324907e-02],
       [ 8.06188664e-02],
       [ 8.04014904e-02],
       [ 8.14630398e-02],
       [ 8.19030855e-02],
       [ 8.15468153e-02],
       [ 8.13899778e-02],
       [ 8.26108326e-02],
       [ 8.21395124e-02],
       [ 8.20904718e-02],
       [ 8.18583360e-02],
       [ 8.10823782e-02],
       [ 8.08224114e-02],
       [ 8.04683636e-02],
       [ 8.06109770e-02],
       [ 7.92873529e-02],
       [ 7.98337774e-02],
       [ 7.90210457e-02],
       [ 7.95093779e-02],
       [ 7.93167692e-02],
       [ 8.06603871e-02],
       [ 8.02207183e-02],
       [ 8.07994279e-02],
       [ 8.11671650e-02],
       [ 8.15260210e-02],
       [ 8.19081466e-02],
       [-2.37235043e-01],
       [-3.35341467e-01],
       [-2.64017808e-01],
       [-2.49194286e-01],
       [-2.58736743e-01],
       [-2.54540777e-01],
       [-2.54004946e-01],
       [-2.51973463e-01],
       [-2.49458453e-01],
       [-2.51690451e-01],
       [-2.50723905e-01],
       [-1.09123491e-01],
       [ 4.74971847e-02],
       [ 8.81222810e-03],
       [-8.77350213e-03],
       [ 1.47537609e-04],
       [ 1.54969587e-03],
       [-7.50191899e-04],
       [ 4.46898540e-04],
       [ 9.71743322e-04],
       [-7.80253909e-05],
       [ 4.52164155e-04],
       [-1.48483134e-04],
       [ 1.51790808e-04],
       [ 5.36924460e-04],
       [-6.48594092e-04],
       [ 4.12357359e-04],
       [ 1.91410460e-03],
       [-3.10860958e-04],
       [-2.88825777e-04],
       [-1.77701768e-04],
       [-4.93614052e-04],
       [-5.27932332e-04],
       [ 4.72870997e-04],
       [ 7.18114852e-04],
       [-1.91691698e-04],
       [-2.11910066e-04],
       [-4.45197024e-04],
       [-6.78286829e-04],
       [-2.18773011e-04],
       [ 3.90128367e-05],
       [-3.27045164e-04],
       [-1.87825061e-04],
       [-6.92302068e-05],
       [ 6.54559699e-05],
       [ 1.25603069e-04],
       [ 6.34867341e-05],
       [ 8.09177515e-05],
       [ 3.23597997e-04],
       [ 2.85269069e-04],
       [ 3.52727970e-04],
       [ 4.55115394e-04],
       [ 5.06720972e-04],
       [-4.69251872e-04],
       [-1.75788575e-04],
       [-1.43521304e-04],
       [ 6.21939797e-05],
       [ 6.99830858e-04],
       [ 3.65534645e-04],
       [ 1.23703806e-03],
       [ 1.74552973e-03],
       [ 1.26530162e-03],
       [ 9.01530762e-04],
       [ 1.38403284e-03],
       [ 3.84661960e-03],
       [ 5.56008667e-02],
       [ 4.86658459e-02],
       [ 4.52697854e-02],
       [ 4.71990081e-02],
       [ 4.74968695e-02],
       [ 4.80804768e-02],
       [ 4.80688621e-02],
       [ 4.82929023e-02],
       [ 4.89882808e-02],
       [ 4.86101551e-02],
       [ 4.86659883e-02],
       [ 4.89641174e-02],
       [ 4.96294909e-02],
       [ 4.94465010e-02],
       [ 5.04511465e-02],
       [ 5.08541047e-02],
       [ 5.04329133e-02],
       [ 5.13707563e-02],
       [ 5.10920063e-02],
       [ 5.04785714e-02],
       [ 5.05102386e-02],
       [ 4.92054428e-02],
       [ 4.94220022e-02],
       [ 4.95178168e-02],
       [ 4.80767419e-02],
       [ 4.83654470e-02],
       [ 4.84533069e-02],
       [ 4.81702839e-02],
       [ 4.75278250e-02],
       [ 4.64708234e-02],
       [ 4.74262455e-02],
       [ 4.70824061e-02],
       [ 4.70188691e-02],
       [ 4.72487977e-02],
       [ 4.80812340e-02],
       [ 4.80731450e-02],
       [ 4.83359503e-02],
       [ 4.87998629e-02],
       [ 4.87626206e-02],
       [ 4.88613086e-02],
       [ 4.92508837e-02],
       [ 4.99193985e-02],
       [ 4.97099304e-02],
       [ 4.94168401e-02],
       [ 4.96188488e-02],
       [ 4.84654802e-02],
       [ 4.87336826e-02],
       [ 4.83092578e-02],
       [ 4.81730567e-02],
       [ 4.78299233e-02],
       [ 5.86405202e-02],
       [ 7.41142481e-02],
       [ 7.27383386e-02],
       [ 7.15958520e-02],
       [ 6.99168851e-02],
       [ 7.19877995e-02],
       [ 7.29198744e-02],
       [ 7.19240505e-02],
       [ 7.28530427e-02],
       [ 7.32389788e-02],
       [ 7.28996970e-02],
       [ 7.22046472e-02],
       [ 7.22206419e-02],
       [ 7.20462276e-02],
       [ 7.09499206e-02],
       [ 7.11773070e-02],
       [ 7.17353904e-02],
       [ 7.07539323e-02],
       [ 7.24375992e-02],
       [ 7.31026846e-02],
       [ 7.31754604e-02],
       [-6.60477839e-02],
       [-9.17790855e-02],
       [-7.76950773e-02],
       [-7.25760121e-02],
       [-7.63688879e-02],
       [-7.64768034e-02],
       [-7.67032250e-02],
       [-7.63951459e-02],
       [-7.58684682e-02],
       [-7.59540668e-02],
       [-7.58977862e-02],
       [-7.50950974e-02],
       [-7.62942229e-02],
       [-7.40648242e-02],
       [-7.54196804e-02],
       [-7.36477061e-02],
       [-7.31164232e-02],
       [-7.37866232e-02],
       [-1.07990942e-02],
       [ 1.24834363e-02],
       [-1.26358518e-03],
       [-3.29197019e-03],
       [-1.74947678e-03],
       [-1.38044734e-03],
       [-2.46724807e-03],
       [-2.68192713e-03],
       [-1.32990865e-03],
       [-1.72537435e-03],
       [ 8.94270665e-02],
       [ 8.84044096e-02],
       [ 7.84850614e-02],
       [ 7.88351364e-02],
       [ 7.93277397e-02],
       [ 8.01198487e-02],
       [ 8.02653149e-02],
       [ 8.06540731e-02],
       [ 8.03504711e-02],
       [ 8.12315057e-02],
       [ 8.14900922e-02],
       [ 8.19331230e-02],
       [ 8.16372952e-02],
       [ 8.15253553e-02],
       [ 8.16494158e-02],
       [ 8.20255568e-02],
       [ 8.26607725e-02],
       [ 8.25440691e-02],
       [ 8.20053555e-02],
       [ 8.20976323e-02],
       [ 8.18850367e-02],
       [ 8.12806225e-02],
       [ 8.13336352e-02],
       [ 8.11027655e-02],
       [ 8.05075728e-02],
       [ 7.95474097e-02],
       [ 7.93082120e-02],
       [ 7.98981236e-02],
       [ 7.92289048e-02],
       [ 7.97981486e-02],
       [ 7.97428082e-02],
       [ 1.98927182e-01],
       [ 2.54892645e-01],
       [ 1.78008887e-01],
       [ 1.09353139e-01],
       [ 1.14675387e-01],
       [ 1.19860483e-01],
       [ 1.20170182e-01],
       [ 1.20225479e-01],
       [ 1.20665320e-01],
       [ 1.20318376e-01],
       [ 1.21185653e-01],
       [ 1.20805460e-01],
       [ 1.19914234e-01],
       [ 1.19541806e-01],
       [ 1.18941436e-01],
       [ 1.18711162e-01],
       [ 1.18463074e-01],
       [ 1.19086311e-01],
       [ 1.19702770e-01],
       [ 1.20438446e-01],
       [-7.14080775e-03],
       [-1.27390695e-02],
       [-1.09796378e-03],
       [ 1.74129556e-04],
       [-2.02501358e-04],
       [-6.60202445e-04],
       [-7.06285951e-05]]

truth_list=[]
for i in range(1000):
    truth_list.append(aa[i][0])
print(truth_list)
print(act_list)

error=[]
x=[]
for i in range(len(truth_list)):
    error.append(truth_list[i]-act_list[i])
    x.append(i)

print('Error:')
print(error)

squarederror=[]
abserror=[]

for val in error:
    squarederror.append(val*val)
    abserror.append(abs(val))

print('squarederror',squarederror)
print('abserror',abserror)
print('MSE=',sum(squarederror)/len(squarederror))

plt.plot(x,truth_list,'r')
plt.plot(x,act_list,'b')

plt.show()


