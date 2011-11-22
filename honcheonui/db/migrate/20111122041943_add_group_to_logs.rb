class AddGroupToLogs < ActiveRecord::Migration
  def change
    add_column :logs, :group, :string
  end
end
