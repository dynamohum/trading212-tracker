require 'rspec'
require 'httparty'
require 'json'

RSpec.configure do |config|
  config.color = true
  config.formatter = :documentation
  
  # Base URL of the running Python application
  # CircleCI or local can set APP_URL if different
  config.add_setting :base_url, default: ENV['APP_URL'] || 'http://localhost:5000'
end
