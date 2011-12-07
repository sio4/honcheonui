class CreateStats < ActiveRecord::Migration
  def change
    create_table :stats do |t|
      t.references :server
      t.integer :cpu_user
      t.integer :cpu_sys
      t.integer :cpu_wait
      t.integer :mem_used
      t.integer :mem_buffer
      t.integer :mem_cached
      t.integer :mem_swpd
      t.integer :proc_total
      t.integer :proc_running
      t.integer :proc_blocked
      t.integer :proc_zombie
      t.integer :users

      t.timestamps
    end
    add_index :stats, :server_id
  end
end
