class Taglink < ActiveRecord::Base
  belongs_to :star, :polymorphic => true
  belongs_to :tag
end
