 % References:
%  [1]: Henk C. Tijms, Stochastic Models: An Algorithmic Approach, 1994. 
%       ID-1 from UC3M library: D 519.216 TIJ.
%       ID-2 from UC3M library: R.1133199.
% 
%  [2]: G. J. Franx, A simple solution for the M/D/c waiting time distribution,  
%       Operations Research Letters 29 (2001) 221-229.
 
%  [3]: Mengwei Xu, Zhe Fu, Xiao Ma, Li Zhang, Yanan Li, Feng Qian, Shangguang Wang, 
%       Ke Li, Jingyu Yang, and Xuanzhe Liu. 2021. From cloud to edge: a first look 
%       at public edge platforms. In Proceedings of the 21st ACM Internet Measurement Conference
%       (IMC '21). Association for Computing Machinery, New York, NY, USA, 37–53.

%% Initialization of system parameters

M = 100; % M the large number after which we substitute the tail behaviour. Koita na diaireitai apo ola ta number of servers
K = 100; % just a natural number, to use as max index within eq. (4.4) in [2] 

service_rate = 1/22.5; 
service_time = 1/service_rate; % in seconds - Deterministic - called D in [1]

step_x = 0.1; %difference (in mseconds) between two consecutive waiting times
max_x = 200; % (in milliseconds)
%temp_vect_x = 0:step_x:(service_time-step_x);

%%% Simulation parameters %%%
target_delay = 100;                   % for 
frac_autonomous = 0.01;                         
lambda_f = 0.03;   
lambdas = linspace(1, 1500, 10);      % 10 lambdas spaced from [0, 1500]      
prop_delay_edge = 18.1;               % edge topology from [3]    
prop_delay_cloud = 22.8;              % 1st cloud topology from [3] 
trans_delay = 0;                      % transmission delay
max_edge = 20;                        % to be defined by us
max_cloud = 40;                       % to be defined by us 
step = 1; 
csvFileName = 'dump_results.csv'; 



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SWEEP THE P(W<=T) FOR DIFFERENT VALUES OF (RHO,C) %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
mu = service_rate;
for rho=0.01:0.01:0.95
    for c=1:max(max_cloud, max_edge)
        disp([c, rho]);
        [xs,CDF] = PT(rho*mu*c, service_time, c, M, K, step_x, max_x);
        writematrix(vertcat(xs, CDF)', sprintf('cdf-sweep/rho-%.2f_c-%d.csv', rho, c));
    end
end



%% 
function [xs,CDF] = PT(arrival_rate, service_time, num_servers, M, K, step_x, max_x) 
    % Computes Pr(T<=x) w/ T being the Waiting(M/D/c) + service(Gamma)
    %
    % returns x vector and CDF(x)
    if num_servers==0
        rel_edge = 0; 
    end 
    num_ser = num_servers;
    tau_vec = 1.01:0.01:100000;
    log_tau_vec = log(tau_vec);
    temp_f_values = arrival_rate*service_time*(1-tau_vec)+num_ser*log(tau_vec);
    abs_temp_f_values = abs(temp_f_values); % I do this because I want the eqn to be eual to zero
    [m,i] = min(abs_temp_f_values);
    tau = tau_vec(i);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%% COMPUTE prob vector %%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Probabilty of having i users in the system = p(i+1)
    temp_vect_x = 0:step_x:max_x;
    [p] = eq_4_4_paper___v3(arrival_rate, service_time, temp_vect_x, num_ser, M, K, tau);
    

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%% Compute P(W<=x) %%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    INF = M;    
    xs = 0:step_x:max_x; 
    i = 1; 
    Wxs = zeros(1,length(xs));
    for i = 1:length(xs)
        Wxs(i) = PW(xs(i), arrival_rate, service_time, num_ser, M, INF, tau, p);
        i = i + 1;
    end
    
    
    %f = sprintf('/home/jorge/Documentos/infocom2023/Data/Wxs_rho-%.2f_c-%d.csv', rho_vector(r), num_ser);
    %writematrix(Wxs, f);
    
    
    %%%%%%%%%%%%%%%%%%%%
    % CONVOLUTION CDFs %
    %%%%%%%%%%%%%%%%%%%%
    
    % (a) Generation of pdf of M/D/c waiting time
    x_analysis = xs;
    Wxs(Wxs>1)=1; %clip to 1 1.0001 values of the P(W<x) CDF
    y_cdf_analysis = [0, Wxs(1:length(x_analysis))];
    y_pdf_analysis = diff(y_cdf_analysis);
    
    
    % (b) Generation of Gamma Distribution samples (video frames) 
    x = x_analysis;
    shape = 16.39974; 
    scale = 15802.78;               % length (bits)  
    cycles_bit = 21.42857143; 
    cycles = cycles_bit*scale;  
    cpu = 250*10^6;                  %Hz 
    time =  1000 * cycles/cpu;  
    y_pdf_gamma = gampdf(x, shape, time); 

    
    %Convoluvion of (a) * (b) - pdf
    convolution = conv(y_pdf_gamma, y_pdf_analysis)*step_x;
    
    % CDF of (a * b) - i.e., integration of pdf -> to get the CDF 
    CDF = cumtrapz(convolution);     %integration of the convolution (CDF)
    
    % Obtain the x-scale
    xs = zeros(1,length(CDF));
    i = 2; xs(1) = 0;
    while i <= length(xs)
        xs(i) = xs(i-1)+step_x;
        %disp(xs(i))
        i = i + 1;
    end   
end

function rel_cloud = CDF_cloud(arrival_rate, pl, service_time, num_servers, target_delay, prop_delay_cloud, trans_delay, M, K, temp_vect_x, step_x) 
    if num_servers==0
        rel_cloud = 0; 
    end 
    arrival_rate = arrival_rate*pl;
    % arr_rate = arrival_rate_matrix(s,r);
    % num_ser = num_servers_vector(s);
    num_ser = num_servers;
    tau_vec = 1.01:0.01:100000;
    log_tau_vec = log(tau_vec);
    temp_f_values = arrival_rate*service_time*(1-tau_vec)+num_ser*log(tau_vec);
    abs_temp_f_values = abs(temp_f_values); % I do this because I want the eqn to be eual to zero
    [m,i] = min(abs_temp_f_values);
    tau = tau_vec(i);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%% COMPUTE prob vector %%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Probabilty of having i users in the system = p(i+1)
    [p] = eq_4_4_paper___v3(arrival_rate, service_time, temp_vect_x, num_ser, M, K, tau);
    
    % Test if P(W<=0) matches
    INF = M;
    %out = PW0(arr_rate, service_time, num_ser, M, INF, tau, p);
    %out2 = bmethod(0, arr_rate, service_time, num_ser, M, INF, tau, p);
    out3 = PW(0, arrival_rate, service_time, num_ser, M, INF, tau, p);
    
    %fprintf('P(W<=0) @paper formula: %f\n', out);
    
    % fprintf('P(W<=x=0) @paper formula: %f\n', out3);
    
    %fprintf('P(W<=0) @p292 Algo.: %f\n', out2);
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%% Compute P(W<=x) %%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    xs = 0:.1:1000; 
    i = 1; 
    Wxs = zeros(1,length(xs));
    for i = 1:length(xs)
        Wxs(i) = PW(xs(i), arrival_rate, service_time, num_ser, M, INF, tau, p);
        i = i + 1;
    end
    
    
    %%%%%%%%%%%%%%%%%%%%
    % CONVOLUTION CDFs %
    %%%%%%%%%%%%%%%%%%%%
    
    % (a) Generation of pdf of M/D/c waiting time
    x_analysis = xs;
    Wxs(Wxs>1)=1; %clip to 1 1.0001 values of the P(W<x) CDF
    y_cdf_analysis = [0, Wxs(1:length(x_analysis))];
    y_pdf_analysis = diff(y_cdf_analysis);
    
    
    % (b) Generation of Gamma Distribution samples (video frames) 
    x = x_analysis;
    shape = 16.39974; 
    scale = 15802.78;               % length (bits)  
    cycles_bit = 21.42857143; 
    cycles = cycles_bit*scale;  
    cpu = 250*10^6;                  %Hz 
    time =  1000 * cycles/cpu;  
    y_pdf_gamma = gampdf(x, shape, time); 

    
    %Convoluvion of (a) * (b) - pdf
    convolution = conv(y_pdf_gamma, y_pdf_analysis)*step_x;
    
    % CDF of (a * b) - i.e., integration of pdf -> to get the CDF 
    CDF = cumtrapz(convolution);     %integration of the convolution (CDF)
    
    % Obtain the x-scale
    xs = zeros(1,length(CDF));
    i = 2; xs(1) = 0;
    while i <= length(xs)
        xs(i) = xs(i-1)+step_x;
        %disp(xs(i))
        i = i + 1;
    end
   
    delay_total = round(target_delay - prop_delay_cloud - trans_delay);  
    % sprintf('delay total: %d', delay_total)
    rel_cloud = CDF(delay_total*10);
    % disp(rel_edge); 
    % m = sprintf('Reliability: %f', reliability);
    % fprintf(fileID, '%d, %.2f, %.6f \n', num_ser, rho_vector(r), reliability);

end

