function [p] = eq_4_4_paper___v3(arrival_rate, service_time, temp_vect_x, num_servers, M, K, tau)
% Compared to v2 of the function: 
% 1. changed part related to eq. 4.4. - currently in comment
% 2. Shifted prob vectors, to have tasks in the QUEUE, instead of tasks in
%    the SYSTEM. Filled with geometrically decreasing probs, to still have M
%    elements.
% 3. Brought back the small increase and renormalization of probabilities,
%    because for something it gave a negative ..^(-17), which when powered to
%    get the geometrically decreasing probs gives complex number.


% put tau instead of dec as input


%% decay factor for last equation <--- done in main, numerically
eta = 1/tau;
decay_factor = 1/(1-eta);


%% Creating matrices for the linear equation system + solving the system
b =  zeros(M, 1);
b(M)=1;

A = zeros(M, M);

for j=0:(M-1)
    
    % tasks already being served
    for k=0:num_servers %min(num_servers,j)
        A(j+1,k+1) = exp(-arrival_rate*service_time)*((arrival_rate*service_time)^j)/(factorial(j)); % exw +1 gt ta index ksekinane apo to 0, gia na piasoun tin periptwsh pou exw 0 tasks mprosta mou
    end
    
    % tasks that wait in the queue
    if j>0 
        for k=(num_servers+1):min((num_servers+j), M-1)
            A(j+1,k+1) = exp(-arrival_rate*service_time)*((arrival_rate*service_time)^(j-k+num_servers))/(factorial(j-k+num_servers)); % exw +1 gt ta index ksekinane apo to 0, gia na piasoun tin periptwsh pou exw 0 tasks mprosta mou
        end
    end

    A(j+1,j+1) = A(j+1,j+1) -1;
end

% to capture the different coefficients for truncated elements, according
% to page 120 of [1].
temp = 0:(M-1);
sum_of_etas_powered_M_2M = sum(eta.^ temp);
A(:, M) = A(:, M)*sum_of_etas_powered_M_2M; 

A(M, :) = ones(1,M); %probabilities summing to one
A(M,M) = decay_factor; % according to eq. in page 120 of [1]





x = linsolve(A,b); % y = A\b; alternative solution of system, even if it is not linear

constraint_violations = 1000*ones(M,1);
for i=1:M
    constraint_violations(i) = b(i) - sum(A(i, :).*x');
end

sum_of_constraint_violations = sum(abs(constraint_violations)); % Just checking accuracy of the solution


% increase so that you don't have negatives and renormalize. Doing this 
% because the solution of the system of equations gives veeeeery small
% negative results, probably due to the numerical nature of the method involved.
temp = x + abs(min(x));
x = temp / sum(temp); %tasks_in_the_queue_probabilities = temp / sum(temp);

p = repmat(x,1);

return;
% figure
% plot (x) 

cumsum_tasks_in_the_SYSTEM_probabilities = cumsum(x); % tasks_in_the_queue_probabilities);

% From tasks in the SYSTEM, to users in the QUEUE. 
cumsum_tasks_in_the_QUEUE_probabilities = cumsum_tasks_in_the_SYSTEM_probabilities(num_servers:M); % indexing starts from 1, but vector semantics from 0. So in position num_servers we have the elements related to num_servers - 1 tasks actually being in the system
% Filling remaining positions with geometrically decreasing probabilities, to still have M tasks in the queue
temp_vect_filling_tasks = zeros(num_servers-1,1);
for t = 1:(num_servers-1)
    temp_vect_filling_tasks(t) = (x(M))^(t*eta);
end
temp_vect_filling_tasks = temp_vect_filling_tasks + cumsum_tasks_in_the_SYSTEM_probabilities(length(cumsum_tasks_in_the_SYSTEM_probabilities));
cumsum_tasks_in_the_QUEUE_probabilities = [cumsum_tasks_in_the_QUEUE_probabilities; temp_vect_filling_tasks];


%figure 
%plot(cumsum_tasks_in_the_QUEUE_probabilities)


% figure
% f1 = plot(cumsum_probabilities);

%% Formula 4.4 from [2]


% step_x = 0.01; %difference between two consecutive waiting times -- commented because moved in main and taken as input here
% temp_vect_x = 0:step_x:(service_time-step_x); -- commented because moved in main and taken as input here
step_k = 1;
temp_vect_k = 1:step_k:(K);

temp_waiting_times = repmat(temp_vect_x, 1, length(temp_vect_k));
waiting_k_index_0 = repmat(temp_vect_k'-1, 1, length(temp_vect_x));
waiting_k_minus_1_index = reshape(waiting_k_index_0', 1,length(temp_waiting_times(1,:)));
waiting_k_minus_1_D_vector = waiting_k_minus_1_index*service_time;
waiting_times = temp_waiting_times +  waiting_k_minus_1_D_vector; 

cum_distr_funcion = zeros(size(waiting_times)); 


for i = 1:length(waiting_times)
    k = waiting_k_minus_1_index(1,i)+1; %min(waiting_k_minus_1_index(1,i)+1, floor(M/num_servers));
    x = waiting_times(1,i);
    temp_exp = exp(-arrival_rate*(k*service_time - x));
    j_vector = 0:min(M-1,(k*num_servers-1)); 
    
    % temp_sum_Q_multiplied_frac = 0;
    % 
    % print_k = k
    % for j=0:min((k*num_servers-1), M-1)
    %     % if k==21
    %     %     print_j = j
    %     %     print_index = k*num_servers-(j+1)-1
    %     % end
    %     Q = cumsum_tasks_in_the_queue_probabilities(k*num_servers-j);%-1); % I put j+1 instead of j, because the indexing starts from 1 in Matlab
    %     frac = arrival_rate^j*(k*num_servers - x)^j/factorial(j);
    %     temp_sum_Q_multiplied_frac = temp_sum_Q_multiplied_frac + Q*frac;
    % end
    % 
    % cum_distr_funcion(1,i) = temp_exp*temp_sum_Q_multiplied_frac;
    % 
    % if i> 2 && cum_distr_funcion(1,i) < cum_distr_funcion(1,i-1)
    %     stop = 1
    % end

    
    M0 = min(length(j_vector), length(find(k*num_servers -j_vector -1 <= M)));
    temp_vect_M1 = find(k*num_servers -j_vector > M); % these will be the elements which I will put following the geometric decay
    M1 = length(temp_vect_M1);
    M1_vector = (M+1):M1; % number of elements that are going to be filled following the geometric decay

    if k*num_servers-1>=0 

        temp_vector_to_sum = power(arrival_rate* ((k)*service_time - x),j_vector) ./ factorial(j_vector);

        if M0>M %100
           stop=1
        end

        if all(k*num_servers -j_vector <= length(cumsum_tasks_in_the_QUEUE_probabilities))            

            Q(1:M0) = cumsum_tasks_in_the_QUEUE_probabilities(k*num_servers -j_vector); %Q = cumsum_tasks_in_the_queue_probabilities(k*num_servers -j_vector); %it has a -1 in eq. 4.4 in [2], but I omit it because we are interested in j starting from 0 and the indexing starts from 1 in matlab

        else %M1>0 

            temp_vector_to_sum = temp_vector_to_sum(1:M);

        end

        temp_dot = sum(Q.*temp_vector_to_sum);
        cum_distr_funcion(1,i) = temp_exp*temp_dot;
        
        % Just checking where ocsillations happen, and how large they are
        % if i>2 && cum_distr_funcion(1,i)< cum_distr_funcion(1,i-1)
        %     oscillation = 1;
        %     oscillating_i = i
        %     if cum_distr_funcion(1,i) < 0.9999
        %         important_decrease = 1
        %     end
        % end

            

    end
end


% max_prob = max(cum_distr_funcion)
if min(cum_distr_funcion) < 0
    min_prob_is_negative = 1
end


% figure
% plot(cum_distr_funcion);

stop=1;
