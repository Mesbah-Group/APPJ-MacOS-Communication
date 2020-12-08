%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Description of the script
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Load data
data = load('2020_12_07_17h05m08s_systemIdentOutputs.csv');


figure()
subplot(4, 1, 1)
plot(data(1,:))
ylabel('T (^\circC)')
subplot(4, 1, 2)
plot(data(2,:))
ylabel('I (a.u.)')
subplot(4, 1, 3)
stairs(data(3,:))
ylabel('P (W)')
subplot(4, 1, 4)
stairs(data(4,:))
ylabel('q (slm)')