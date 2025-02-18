import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import signal

signal_duration = 10

# defining the common parameters
A = 1
N = 11  # Sum of last 2 digits of ID
start_time = 0
stop_time = 1
f_carrier = 1000  # different from the problem statement to avoid the upper-lower sideband interference
kf = 100  # V/Hz
Am_max = 10
Am_min = 1
# FOR LAB 7, THE PART THAT FOLLOWS IS NOT IN THE PROBLEM, IT WAS DONE FOR CONTINUATION TO THE PREVIOUS
# LABS WHICH HAD DEMODULATION.

# Modelling noise
mu = 0
# If receiver doesn't know the carrier, estimate the subtraction term

receiverKnowsCarrier = True
for T in range(signal_duration):
    Am = np.random.randint(Am_min, Am_max + 1)
    # B = 2 * (kp * max(mp)/(2 * pi) + B), and in our case mp is a sinusoid, so max(mp) = 1*Am
    B_sig = 2 * (Am_max * kf/(2 * math.pi) + N)
    fs = 10 * B_sig
    ts = 1 / fs
    time = np.arange(start_time, stop_time, ts)

    len_time = len(time)
    freq_axis = np.linspace(-fs / 2, fs / 2, len_time)

    # Defining the message signal and time
    message_t = Am * np.cos(2 * math.pi * N * time)
    message_integrated_t = ts * np.cumsum(message_t)
    message_f = np.fft.fftshift(abs(np.fft.fft(message_t) / fs))

    # Modulating the message signal
    message_mod_t = A * np.cos(2 * math.pi * f_carrier * time + kf * message_integrated_t)
    message_mod_f = np.fft.fftshift(abs(np.fft.fft(message_mod_t) / fs))

    sigma_square = 10**(-4)
    sigma = np.sqrt(sigma_square)
    noise = mu + sigma * np.random.randn(len(message_t))

    # Modelling the Channel - Multiplied with carrier to shift it to the carrier frequency.
    B = 2 * B_sig
    channel_t = np.multiply(2 * B * np.sinc(2 * B * (time - (start_time + stop_time) / 2)),
                            2 * np.cos(2 * math.pi * f_carrier * time))
    output_t = np.convolve(message_mod_t, channel_t, mode='same') / fs
    output_f = np.fft.fftshift(abs(np.fft.fft(output_t) / fs))

    # Demodulation using Hilbert detector - uncomment any one at a time to run.
    # Method 1 - From BP Lathi

    # output_predemod_t = np.diff(output_t, prepend=output_t[0])/(ts * kf)
    # output_demod_t = np.abs(signal.hilbert(output_predemod_t)) - np.mean(np.abs(signal.hilbert(output_predemod_t)))
    # output_demod_f = np.fft.fftshift(abs(np.fft.fft(output_demod_t) / fs))

    # Method 2 -
    # https://www.gaussianwaves.com/2017/06/phase-demodulation-using-hilbert-transform-application-of-analytic-signal/

    output_predemod_t = signal.hilbert(output_t)  # form the analytical signal from the received vector
    inst_phase = np.unwrap(np.angle(output_predemod_t))  # instantaneous phase

    if receiverKnowsCarrier:
        offsetTerm = 2 * math.pi * f_carrier * time  # if carrier frequency & phase offset is known
    else:
        p = np.poly1d(np.polyfit(time, inst_phase, 1))  # linearly fit the instantaneous phase
        offsetTerm = p(time)  # re-evaluate the offset term using the fitted values
    output_predemod_t = (inst_phase - offsetTerm) / (kf*ts)
    output_demod_t = np.diff(output_predemod_t, prepend=output_predemod_t[0])
    output_demod_f = np.fft.fftshift(abs(np.fft.fft(output_demod_t) / fs))

    # Some samples from the beginning and the end of the signal are removed while plotting the demodulated signal,
    # because the np.diff() function doesn't act on the first and the last term, hence leaving some edge residues.
    plt.figure(1)
    plt.subplots_adjust(top=0.933, bottom=0.104, left=0.057, right=0.988, hspace=1.0, wspace=0.2)
    plt.subplot(4, 1, 1)
    plt.plot(time + T, message_t)
    plt.title('Message signal time domain')
    plt.xlabel('time(t)')
    plt.ylabel('Amplitude')

    plt.subplot(4, 1, 2)
    plt.plot(time + T, message_mod_t)
    plt.title('Modulated signal time domain')
    plt.xlabel('time(t)')
    plt.ylabel('Amplitude')

    plt.subplot(4, 1, 3)
    plt.plot(time + T, output_t)
    plt.title('Modulated signal after the channel time domain')
    plt.xlabel('time(t)')
    plt.ylabel('Amplitude')

    plt.subplot(4, 1, 4)
    plt.plot(time[int(fs*0.001):-int(fs*0.001)] + T, output_demod_t[int(fs*0.001):-int(fs*0.001)])
    plt.title('Demodulated signal time domain')
    plt.xlabel('time(t)')
    plt.ylabel('Amplitude')

    plt.figure(2)
    plt.subplots_adjust(top=0.933, bottom=0.104, left=0.057, right=0.988, hspace=1.0, wspace=0.2)
    plt.subplot(4, 1, 1)
    plt.plot(freq_axis, message_f)
    plt.title('Message signal frequency domain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim([-4 * N, 4 * N])

    plt.subplot(4, 1, 2)
    plt.plot(freq_axis, message_mod_f)
    plt.title('Modulated signal frequency domain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim([-(f_carrier + 2 * B_sig), f_carrier + 2 * B_sig])

    plt.subplot(4, 1, 3)
    plt.plot(freq_axis, output_f)
    plt.title('Modulated signal after the channel frequency domain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim([-(f_carrier + 2 * B_sig), f_carrier + 2 * B_sig])

    plt.subplot(4, 1, 4)
    plt.plot(freq_axis[int(fs*0.001):-int(fs*0.001)], output_demod_f[int(fs*0.001):-int(fs*0.001)])
    plt.title('Demodulated signal frequency domain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim([-4 * N, 4 * N])

plt.show()
