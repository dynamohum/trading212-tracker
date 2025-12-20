require 'spec_helper'

RSpec.describe 'Trading212 Tracker API' do
  let(:base_url) { RSpec.configuration.base_url }

  context 'GET /api/positions' do
    it 'returns a list of positions' do
      response = HTTParty.get("#{base_url}/api/positions")
      
      # Expect 200 OK
      expect(response.code).to eq(200)
      
      body = JSON.parse(response.body)
      expect(body).to have_key('items')
      expect(body['items']).to be_an(Array)
      expect(body).to have_key('mode')
    end
  end

  context 'GET /api/returns' do
    it 'returns calculate returns object' do
      response = HTTParty.get("#{base_url}/api/returns")
      expect(response.code).to eq(200)
      
      body = JSON.parse(response.body)
      expect(body).to be_a(Hash)
    end
  end

  context 'GET /api/settings' do
    it 'returns application settings' do
      response = HTTParty.get("#{base_url}/api/settings")
      expect(response.code).to eq(200)
      
      body = JSON.parse(response.body)
      expect(body).to have_key('tracking')
      expect(body).to have_key('hidden_tickers')
      expect(body['hidden_tickers']).to be_an(Array)
    end
  end
  
  context 'POST /api/settings' do
    it 'updates settings successfully' do
       # Toggle tracking to verify write
       response = HTTParty.post(
         "#{base_url}/api/settings", 
         body: { tracking: false }.to_json,
         headers: { 'Content-Type' => 'application/json' }
       )
       expect(response.code).to eq(200)
       expect(JSON.parse(response.body)['status']).to eq('updated')
       
       # Verify it changed
       check = HTTParty.get("#{base_url}/api/settings")
       expect(JSON.parse(check.body)['tracking']).to be(false)
    end
  end
end
