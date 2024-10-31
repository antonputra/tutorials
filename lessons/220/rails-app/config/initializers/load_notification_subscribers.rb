Dir[Rails.root.join('app', 'subscribers', '**', '*_subscriber.rb')].each do |subscriber_file|
    require subscriber_file
  end
