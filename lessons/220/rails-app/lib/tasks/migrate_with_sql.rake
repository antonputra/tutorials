namespace :db do
    desc 'Make migration with output'
    task(:migrate_with_sql => :environment) do
      ActiveRecord::Base.logger = Logger.new(STDOUT)
      Rake::Task['db:migrate'].invoke
    end
  end