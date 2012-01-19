class CreateTaglinks < ActiveRecord::Migration
  def change
    create_table :taglinks do |t|
      t.string :name
      t.text :description
      t.references :star, :polymorphic => true
      t.references :tag

      t.timestamps
    end
    add_index :taglinks, :star_id
    add_index :taglinks, :tag_id
  end
end
