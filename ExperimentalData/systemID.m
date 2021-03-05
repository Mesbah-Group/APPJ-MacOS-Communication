%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script reads data from a csv file to identify a state space system.
% x(k+1) = A*x(k) + B*u(k)
% y(k) = C*x(k)
% 
% Inputs:
% * file name of csv file where data is located
%
% Outputs:
% * A, B, C matrices corresponding to process form with state feedback
% * nominal steady state values
% * maximum errors between linear model and data
% * minimum errors between linear model and data
% * information on the performance metrics of the identified model
% * copy of information on the data used
%  
% REQUIREMENTS:
% * MATLAB R2019b or later (?)
% * System Identification Toolbox
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% USER INPUTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
filename = '2020_12_07_17h05m08s_systemIdentOutputs.csv';
filedate = filename(1:20);
data_direction = 1; % 0 for column-wise data, 1 for row-wise data
y_idxs = [1,2]; % row/column indices in the data file corresponding to the output data
u_idxs = [3,4]; % row/column indices in the data file corresponding to the input data

% labels corresponding to the data
y_labels = {'T (^\circC)', 'I (a.u.)'}; % outputs
u_labels = {'P (W)', 'q (slm)'}; % inputs

Ts = 0.5; % Sampling time

norm_intensity = 1; % 1 for yes, 0 for no
I_col = 2; % column/row in which the intensity data is located, leave as 
% empty if not specified
I_norm_factor = 1/25000*3e6; % intensity normalization factor
plot_fit = 1; % 1 for yes, 0 for no; plot a comparison of the data 
% and identified model
center_data = 1; % 1 for yes, 0 for no
num_pts2center = 10; % number of points to use to center the data

est_function = 'ssest'; % choose 'ssest' or 'n4sid'

validate_sys = 0;   % option to validate data (1 for yes, 0 for no)
valid_split = 0.3;  % validation split, i.e. how much of the data to reserve for validation

saveModel = 0; % 1 for yes, 0 for no
% specify an output file name, otherwise a default is used; please include 
% '.mat' in your filename
out_filename = [];


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MAIN SCRIPT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Load data
data = load(filename);
if data_direction
    data = data'; % transpose data if row-wise
end

%% Clean data
% remove startup data
data = data(5:end,:);
% normalize intensity if desired
if norm_intensity
    if isempty(I_col)
        warning('Row/column for Intensity is not specified even though normalization was requested. Intensity data NOT normalized.')
    else
        data(:,I_col) = data(:,I_col)./I_norm_factor;
    end
end

%% Plot data to visualize it
disp('Plotting data to visualize it... See Figure 1 and 2 to verify data.')
figure(1)
ny = length(y_idxs);
for i = 1:ny
    subplot(ny, 1, i)
    plot(data(:,y_idxs(i)))
    ylabel(y_labels{i})
end
xlabel('Time Step')

figure(2)
nu = length(u_idxs);
for i = 1:nu
    subplot(nu, 1, i)
    stairs(data(:,u_idxs(i)))
    ylabel(u_labels{i})
end
xlabel('Time Step')

%% split data into training and validation
if validate_sys
    [nData, ~] = size(data);
    trainIdx = round(nData*(1-valid_split));
    v_ydata = data(trainIdx+1:end,y_idxs);
    v_udata = data(trainIdx+1:end,u_idxs);
    ydata = data(1:trainIdx,y_idxs);
    udata = data(1:trainIdx,u_idxs);
else
    % split data into input and output data
    udata = data(:,u_idxs);
    ydata = data(:,y_idxs);
end

%% Identify the model
disp('Identifying the model...')
if center_data
    % Translate to origin
    uss = mean(udata(1:num_pts2center,:), 1);
    yss = mean(ydata(1:num_pts2center,:), 1);
    disp(['Input nominal steady states: ', num2str(uss)])
    disp(['Output nominal steady states: ', num2str(yss)])

    % Work with deviation variables
    udata = udata - uss;
    ydata = ydata - yss;
    if validate_sys
        v_udata = v_udata - uss;
        v_ydata = v_ydata - yss;
    end
else
    warning('Steady states not calculated! Data not centered.')
end

modelOrder = 2;
subIDdata = iddata(ydata, udata, Ts);
Ndata = subIDdata.N;

if strcmpi(est_function, 'ssest')
    opt = ssestOptions;
    opt.SearchOptions.Tolerance = 1e-8;
    opt.OutputWeight = [100,0;0,1];
    sys = ssest(subIDdata,modelOrder, 'DisturbanceModel', 'none', ...
        'Form', 'canonical', 'Ts', Ts);
%     sys = ssest(subIDdata,modelOrder, 'DisturbanceModel', 'none', ...
%         'Form', 'canonical', 'Ts', Ts, opt);
elseif strcmpi(est_function, 'n4sid')
    sys = n4sid(subIDdata, modelOrder, 'DisturbanceModel', 'none', ...
        'Form', 'canonical', 'Ts', Ts);
else
    warning('Invalid estimation function! Using ''ssest''...')
    opt = ssestOptions('OutputWeight', [1,0;0,1]);
    sys = ssest(subIDdata,modelOrder, 'DisturbanceModel', 'none', ...
        'Form', 'canonical', 'Ts', Ts);
end

A = sys.A;
B = sys.B;
C = sys.C;

if plot_fit
    % Verify the model graphically
    disp('Verifying model graphically... See Figure 3.')
    simTime = 0:Ts:Ts*(Ndata-1);
    yCompare = lsim(sys, udata, simTime);

    opt = compareOptions('InitialCondition', zeros(modelOrder,1));
    figure(3)
    compare(subIDdata, sys, opt)
    xlabel('Time/s')
    legend('Experimental Data', 'Linear Model')
    title('Trained Model')
    
    % plot the validation
    if validate_sys
        disp('Validating model... See Figure 4.')
        [NdataSim, ~] = size(v_udata);
        v_simTime = 0:Ts:Ts*(NdataSim-1);
        v_subIDdata = iddata(v_ydata, v_udata, Ts);
        v_x0 = ydata(end,:);
        v_yCompare = lsim(sys, v_udata, v_simTime, v_x0);

        figure(4)
        opt = compareOptions('InitialCondition', v_ydata(1,:)');
        compare(v_subIDdata, sys, opt)
        legend('Validation Data', 'Linear Model')
        xlabel('Time/s')
        title('Validation')
    end
end

wmaxTrain = max(ydata-yCompare);
wminTrain = min(ydata-yCompare);

% validate model
% TODO ...
wmaxValid = zeros(1,ny);
wminValid = zeros(1,ny);

% determine max and min errors
maxErrors = max([wmaxTrain; wmaxValid], [], 1);
minErrors = min([wminTrain; wminValid], [], 1);
disp(['Maximum Output Errors: ', num2str(maxErrors)])
disp(['Minimum Output Errors: ', num2str(minErrors)])

%% save model if specified
% save information on the data
dataInfo.yLabels = y_labels;    % user-defined labels for the outputs
dataInfo.uLabels = u_labels;    % user-defined labels for the inputs
dataInfo.samplingTime = Ts;     % sampling time from the data
dataInfo.fileName = filename;   % file name of where the data was taken
dataInfo.InormFactor = I_norm_factor;   % normalization factor for intensity data

% save information on the performance of the identified model


if saveModel
    % if output filename is not specified, generate one from a default
    if isempty(out_filename)
        out_filename = ['APPJmodel_', filedate, '.mat'];
    end
    
    % check if the file already exists to ensure no overwritten files
    if isfile(out_filename)
        overwrite_file = input('Warning: File already exists in current path! Do you want to overwrite? [1 for yes, 0 for no]: ');
        if overwrite_file
            save(out_filename, 'A', 'B', 'C', 'yss', 'uss', 'maxErrors', 'minErrors', 'dataInfo')
        else
            out_filename = input('Input a new filename (ensure .mat is included in your filename) or press Enter if you no longer want to save the identified model: \n', 's');
            if isempty(out_filename)
                disp('Identified system not saved.')
            else
                save(out_filename, 'A', 'B', 'C', 'yss', 'uss', 'maxErrors', 'minErrors', 'dataInfo')
            end
        end
    else
        save(out_filename, 'A', 'B', 'C', 'yss', 'uss', 'maxErrors', 'minErrors', 'dataInfo')
    end
end

