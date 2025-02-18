import numpy as np
import matplotlib.pyplot as plt
import math


def rect_pulse(freq, pulse_width):
    return np.where(abs(freq) <= pulse_width/2, 1, 0)


time_endpt = 30
# Defining all the common parameters for each second
start_time = 0
stop_time = 1
f_carrier = 1000
N = 20  # Sum of last 3 digits of the ID
# Modelling the channel - Multiplied with carrier to shift it to the carrier frequency.
B1 = 300
# The following can also be used as an alternative method. Uncomment this and the output_f using np.multiply.
# channel_f = rect_pulse(freq_axis, 2 * B1)  # Done using a rectangular pulse
# channel_f = np.fft.fftshift(np.abs(np.fft.fft(channel_t)/fs)) # Done using the fft of sinc pulse
# Either of the two ways mentioned above can be used, and they give identical results

# Modelling noise
mu = 0  # Sum of last two digits of ID
sigma_square = 0.01  # Sum of last three digits of ID
# Alternately:
# output_f = np.multiply(channel_f, message_mod_f)

# Demodulation
B_LPF = 300
for T in range(time_endpt):
    fs = 10 * f_carrier
    ts = 1 / fs
    time = np.arange(start_time, stop_time, ts)
    # Frequency axis
    time_len = len(time)
    freq_axis = np.linspace(-fs / 2, fs / 2, time_len)

    # Defining the carrier signal
    carrier_signal_t = 2 * np.cos(2 * math.pi * f_carrier * time)
    carrier_signal_f = np.fft.fftshift(abs(np.fft.fft(carrier_signal_t)/fs))

    # Choosing a different message signal
    selector = np.random.randint(1, 4)

    # Generating the message signal
    if selector == 1:
        message_t = np.cos(2 * N * (time - (-start_time + stop_time) / 2))
    elif selector == 2:
        message_t = 2 * N * np.sinc(2 * N * (time - (-start_time + stop_time) / 2))
    elif selector == 3:
        message_t = np.zeros_like(time)
        message_t[:] = 200 * np.cos(np.pi*200*(time[:] - (-start_time + stop_time) / 2))\
                       / (1 - (2 * 200*(time[:] - (-start_time + stop_time) / 2))**2) \
                       * np.sinc(200*(time[:] - (-start_time + stop_time) / 2))

    message_f = np.fft.fftshift(abs(np.fft.fft(message_t) / fs))

    # Modulating the message signal
    message_mod_t = np.multiply(message_t, carrier_signal_t)
    message_mod_f = np.fft.fftshift(abs(np.fft.fft(message_mod_t)/fs))

    channel_t = np.multiply(2 * B1 * np.sinc(2 * B1 * (time - (start_time + stop_time) / 2)), carrier_signal_t)
    sigma = math.sqrt(sigma_square)
    noise = mu + sigma * np.random.randn(len(message_t))

    # Passing the modulated signal through a band limited channel
    # Modify the amplitude of the noise signal and see the effect
    output_t = np.convolve(message_mod_t, channel_t, mode='same')/fs + noise
    output_f = np.fft.fftshift(abs(np.fft.fft(output_t)/fs))
    output_predemod_t = np.multiply(output_t, carrier_signal_t / 2)
    LPF_t = 2 * B_LPF * np.sinc(2 * B_LPF * (time - (start_time + stop_time) / 2))
    output_demod_t = np.convolve(LPF_t, output_predemod_t, mode='same')/fs

    output_predemod_f = np.convolve(output_f, carrier_signal_f / 2, mode='same')
    LPF_f = rect_pulse(freq_axis, 2 * B_LPF)
    output_demod_f = np.multiply(output_predemod_f, LPF_f)

    # Time domain plots
    plt.figure(1)
    plt.subplots_adjust(top=0.933, bottom=0.104, left=0.051, right=0.988, hspace=0.798, wspace=0.2)
    plt.subplot(3, 1, 1)
    plt.plot(time + T, message_t)
    plt.title('Message - Time Domain')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 2)
    plt.plot(time + T, message_mod_t)
    plt.title('Modulated Output - Time Domain')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 3)
    plt.plot(time + T, output_demod_t)
    plt.title('Demodulated Output - Time Domain')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    # Frequency domain plots
    plt.figure(2)
    plt.subplots_adjust(top=0.933, bottom=0.104, left=0.051, right=0.988, hspace=0.798, wspace=0.2)
    plt.subplot(3, 1, 1)
    plt.plot(freq_axis, message_f)
    plt.title('Message - Frequency Domain')
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 2)
    plt.plot(freq_axis, message_mod_f)
    plt.title('Modulated Output - Frequency Domain')
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 3)
    plt.plot(freq_axis, output_demod_f)
    plt.title('Demodulated Output - Frequency Domain')
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')

    # plt.pause(1)

plt.show()
