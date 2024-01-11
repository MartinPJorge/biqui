function out = PW(x, arrival_rate, service_time, num_servers, M, INF, tau, p)

    lambda = arrival_rate;
    D = service_time;
    c = num_servers;

    % Find k s.t.: (k-1)D <= x < kD
    k = 0;
    while not ((k-1)*D <= x && x < k*D)
        k = k+1;
    end

    % % Use the tau decay to fill missing pj's
    MAX_K = k*c-+1;
    p_ = zeros(1,MAX_K);
    for j = 1:max(M, k*c+1)
        if j>M
            p_(j) = p(M-1) * tau^(M-j);
        else
            p_(j) = p(j);
        end
    end
    p = repmat(p_, 1);

    %disp(k);

    % Compute the probability of having q=i users enqueued
    q = zeros(1,length(p));
    q(1) = sum(p(1:c+1));
    for i = 2:length(p)-c
        q(i) = p(i+c);
    end

    % Create the CUMSUM queue vector
    Q = zeros(1,INF);
    for i = 1:k*c
        Q(i) = sum(q(1:i));
    end

    % Compute P(W<=0)
    PW0_ = 0;
    for j_ = 1:k*c
        j = j_-1;
        PW0_ = PW0_ + Q(k*c-j_+1) * lambda^j * (k*D-x)^j / factorial(j);
    end
    PW0_ = PW0_ * exp(-lambda*(k*D-x));

    out = PW0_;
end
