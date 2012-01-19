class CreateTags < ActiveRecord::Migration
  def change
    create_table :tags do |t|
      t.string	:name,		:null => false
      t.text	:description
      t.string	:category,	:default => 'tag'

      t.timestamps
    end
  end
end
