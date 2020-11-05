#!/usr/bin/env ruby


# as per https://developer.github.com/v3/guides/discovering-resources-for-a-user/#dont-rely-on-public-organizations
# github explicitly says that this is the way to find *all* user's organizations, including private ones. 
# So, guess what it doesn't do? Find private organizations.



require 'octokit'
Octokit.auto_paginate = true
client = Octokit::Client.new :access_token => ENV["OAUTH_ACCESS_TOKEN"]
client.organizations.each do |organization|
  puts "User belongs to the #{organization[:login]} organization."
end
