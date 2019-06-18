#coding:utf-8
import numpy as np
from math import pi
import matplotlib.pyplot as plt
import math
from scipy import fftpack
from sklearn import preprocessing
import neurolab as nl


# ��Ԫ��
size = 10
sampling_t = 0.01

t = np.arange(0, size, sampling_t)

#��������ź�����
a = np.random.randint(0, 2, size)   #���������������

m = np.zeros(len(t), dtype=np.float32)    #����һ��������״�����͵���0��������
for i in range(len(t)):
    m[i] = a[int(math.floor(t[i]))]


def awgn(y, snr):      #snrΪ�����dBֵ
    snr = 10 ** (snr / 10.0)
    xpower = np.sum(y ** 2) / len(y)
    npower = xpower / snr
    return np.random.randn(len(y)) * np.sqrt(npower) + y

def feature_rj(y):         #[feature1, f2, f3] = rj(noise_bpsk, fs)
    global R,J
    global r,j
    h = fftpack.hilbert(y)   # hilbert�任
    z = np.sqrt(y**2 + h**2)   # ����
    m2 = np.mean(z**2)     # ����Ķ��׾�
    m4 = np.mean(z**4)     # ������Ľ׾�
    r = abs((m4-m2**2)/m2**2)
    Ps = np.mean(y**2)/2
    j = abs((m4-2*m2**2)/(4*Ps**2))
    return (r,j)

def feature_Bispectrum(y):
    global s,Z
    ly = size  # ����10
    nrecs = np.int64(1 / sampling_t)  # ����100
    nlag = 20
    nsamp = nrecs  # ÿ��������100
    nrecord = size
    nfft = 128
    Bspec = np.zeros((nfft, nfft), dtype=np.float32)
    y = y.reshape(ly, nrecs)
    c3 = np.zeros((nlag + 1, nlag + 1), dtype=np.float32)
    ind = np.arange(nsamp)

    for k in range(nrecord):
        x = y[k][ind]
        x = x - np.mean(x)
        for j in range(nlag + 1):
            z = np.multiply(x[np.arange(nsamp - j)], x[np.arange(j, nsamp)])
            for i in range(j, nlag + 1):
                sum = np.mat(z[np.arange(nsamp - i)]) * np.mat(x[np.arange(i, nsamp)]).T
                sum = sum / nsamp
                c3[i][j] = c3[i][j] + sum  # i,j˳��
    c3 = c3 / nrecord

    c3 = c3 + np.mat(np.tril(c3, -1)).T  # ȡ�Խ�����������,c3Ϊ����
    c31 = c3[1:, 1:]
    c32 = np.mat(np.zeros((nlag, nlag), dtype=np.float32))
    c33 = np.mat(np.zeros((nlag, nlag), dtype=np.float32))  # ������ֱ��3�����
    c34 = np.mat(np.zeros((nlag, nlag), dtype=np.float32))
    for i in range(nlag):
        x = c31[i:, i]
        c32[nlag - 1 - i, 0:nlag - i] = x.T
        c34[0:nlag - i, nlag - 1 - i] = x
        if i < (nlag - 1):
            x = np.flipud(x[1:, 0])  # ���·�ת,��ת����ȻΪ����
            c33 = c33 + np.diag(np.array(x)[:, 0], i + 1) + np.diag(np.array(x)[:, 0], -(i + 1))
    c33 = c33 + np.diag(np.array(c3)[0, :0:-1])
    cmat = np.vstack((np.hstack((c33, c32, np.zeros((nlag, 1), dtype=np.float32))),
                      np.hstack((np.vstack((c34, np.zeros((1, nlag), dtype=np.float32))), c3))))          #41*41
    Bspec = fftpack.fft2(cmat, [nfft, nfft])      #2ά����Ҷ�任
    Bspec = np.fft.fftshift(Bspec)                #128*128

    waxis = np.arange(-nfft / 2, nfft / 2) / nfft
    X, Y = np.meshgrid(waxis, waxis)
    plt.contourf(X, Y, abs(Bspec))
    plt.contour(X, Y, abs(Bspec))
    Z.append(np.mean(abs(Bspec)))
    #s_content = './s��ʼ��λ�ı�/'
    #plt.savefig(s_content.decode("utf-8").encode("gbk") +  str(s) + '.jpg')
    #plt.show()
    return Bspec


def features(s):
#    for mc in range(2):
        snr = np.random.uniform(0, 20)       #��һ�����ȷֲ��������������������ҿ�--[low,high)
        #s = awgn(s,snr)            #��ԭʼ�źŵĻ���������SNR����ȵ�����
        rj = np.array(feature_rj(s))               #����R,J����
        z = feature_Bispectrum(s)                  #����˫������������ͼ��
        xx = np.int64(np.sqrt(np.size(z))/2)
        z = np.array(z[:xx,xx:])
        z = np.tril(z).real               #ȡ����z��ʵ��
        bis = np.zeros((1, xx),dtype=np.float32)    #����
        for i in range(xx):
            for j in range(xx-i):
                bis[0][i] = bis[0][i]+z[xx-1-j][i+j]
        m = bis[0].reshape(1,xx)
        normalized = preprocessing.normalize(m)[0,:]    #������������ֵ���Ը�������ֵ��ƽ��֮��
        features = np.hstack((rj,normalized))           #�ϲ�����r,j��normalized
        return features

        
R = []
J = []
ts1 = np.arange(0, (np.int64(1/sampling_t) * size))/(10*(m+1))
W = []
Z = []
for i in range(0,40,1):
    W.append(i / (2 * pi))

for s in W:
    global r,j
    fsk = np.cos(np.dot(2 * pi, ts1) + s)
    features(fsk)
    R.append(r)
    J.append(j)
plt.plot(W, R, color='green', label='1')
plt.legend() # ��ʾͼ��
plt.xlabel('s[0-2 * pi]')
plt.ylabel('R')
plt.show()
plt.plot(W, J, color='red', label='2')
plt.legend() # ��ʾͼ��
plt.xlabel('s[0-2 * pi]')
plt.ylabel('J')
plt.show()


plt.plot(W, Z, color='red', label='3')
plt.legend() # ��ʾͼ��
plt.xlabel('A[0-2 * pi]')
plt.ylabel('trend')
plt.show()






z1 = np.polyfit(W, R, 3) # ��3�ζ���ʽ���
p1 = np.poly1d(z1)
print(p1) # ����Ļ�ϴ�ӡ��϶���ʽ
yvals=p1(W) # Ҳ����ʹ��yvals=np.polyval(z1,x)

z2 = np.polyfit(W, J, 3) # ��3�ζ���ʽ���
p2 = np.poly1d(z2)
print(p2) # ����Ļ�ϴ�ӡ��϶���ʽ
yvals2=p2(W) # Ҳ����ʹ��yvals=np.polyval(z1,x)

plot1=plt.plot(W, R, '*',label='original values')
plot2=plt.plot(W, yvals, 'r',label='polyfit values')
plt.xlabel('W axis')
plt.ylabel('R axis')
plt.legend(loc=4) # ָ��legend��λ��,���߿����Լ�help�����÷�
plt.title('polyfitting')
plt.show()
plt.savefig('p1.png')

plot1=plt.plot(W, J, '*',label='original values')
plot2=plt.plot(W, yvals2, 'r',label='polyfit values')
plt.xlabel('W axis')
plt.ylabel('J axis')
plt.legend(loc=4) # ָ��legend��λ��,���߿����Լ�help�����÷�
plt.title('polyfitting')
plt.show()
plt.savefig('p2.png')