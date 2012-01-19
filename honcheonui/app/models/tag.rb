class Tag < ActiveRecord::Base
	validates :name,	:presence => true

	has_many :taglinks
	has_many :servers, :through => :taglinks, :source => :star, :source_type => 'Server'

end
