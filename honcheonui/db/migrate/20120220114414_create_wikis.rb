class CreateWikis < ActiveRecord::Migration
  def change
    create_table :wikis do |t|
      t.string :name
      t.text :source
      t.references :wiki
      t.integer :version
      t.string :topic
      t.references :user

      t.timestamps
    end
    add_index :wikis, :wiki_id
    add_index :wikis, :user_id
  end
end
