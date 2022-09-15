title 'Ensure my-app is properly installed and running'

    describe file('/etc/systemd/system/my-app.service') do
        it { should exist }
    end

    describe service('my-app') do
        it { should be_installed }
        it { should be_enabled }
        it { should be_running }
    end
