import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api/auth";

export default function MenuBuilder() {
  const { id } = useParams();
  const [menu, setMenu] = useState(null);
  const [newCategory, setNewCategory] = useState("");
  const [editingItem, setEditingItem] = useState(null); // {categoryId, itemId}

  // Load menu
  useEffect(() => {
    API.get(`/events/${id}/menu/`).then(res => setMenu(res.data));
  }, [id]);

  // Add new category
  const addCategory = async () => {
    if (!newCategory) return;

    const res = await API.post("/menu/categories/", {
      menu: menu.id,
      name: newCategory,
    });

    setMenu(prev => ({
      ...prev,
      categories: [...prev.categories, res.data],
    }));
    setNewCategory("");
  };

  // Add new item
  const addItem = async (categoryId) => {
  // create item on backend
  const res = await API.post("/menu/items/", {
    category: categoryId,
    name: "New item",
    price: 0,
    description: "",
  });

  // update frontend state with returned item (contains real id)
  setMenu(prev => ({
    ...prev,
    categories: prev.categories.map(cat =>
      cat.id === categoryId
        ? { ...cat, items: [...cat.items, res.data] }
        : cat
    ),
  }));
};


  // Save item
  const saveItem = async (categoryId, item) => {
  try {
    const res = await API.patch(`/menu/items/${item.id}/`, {
      name: item.name,
      price: parseFloat(item.price) || 0,
      description: item.description || "",
    });

    // Update state with backend response
    setMenu(prev => ({
      ...prev,
      categories: prev.categories.map(cat =>
        cat.id === categoryId
          ? {
              ...cat,
              items: cat.items.map(i =>
                i.id === item.id ? res.data : i
              ),
            }
          : cat
      ),
    }));

    setEditingItem(null);
    alert("Item saved successfully!");
  } catch (err) {
    console.error(err.response?.data || err);
    alert("Failed to save item. Check console for details.");
  }
};



  if (!menu) return <p>Loading menu…</p>;

  return (
    <div style={styles.page}>
      <h2>{menu.title || "Menu Builder"}</h2>

      {menu.categories.map(cat => (
        <div key={cat.id} style={styles.card}>
          <h3>{cat.name}</h3>

          {cat.items.map(item => {
            const isEditing = editingItem?.itemId === item.id;
            return (
              <div key={item.id} style={styles.itemRow}>
                <input
                  style={styles.input}
                  value={item.name}
                  disabled={!isEditing}
                  onChange={(e) =>
                    setMenu(prev => ({
                      ...prev,
                      categories: prev.categories.map(c =>
                        c.id === cat.id
                          ? {
                              ...c,
                              items: c.items.map(i =>
                                i.id === item.id
                                  ? { ...i, name: e.target.value }
                                  : i
                              ),
                            }
                          : c
                      ),
                    }))
                  }
                  placeholder="Item Name"
                />

                <input
                  style={styles.price}
                  type="number"
                  value={item.price}
                  disabled={!isEditing}
                  onChange={(e) =>
                    setMenu(prev => ({
                      ...prev,
                      categories: prev.categories.map(c =>
                        c.id === cat.id
                          ? {
                              ...c,
                              items: c.items.map(i =>
                                i.id === item.id
                                  ? { ...i, price: e.target.value }
                                  : i
                              ),
                            }
                          : c
                      ),
                    }))
                  }
                  placeholder="Price"
                />

                <input
                  style={styles.input}
                  value={item.description}
                  disabled={!isEditing}
                  onChange={(e) =>
                    setMenu(prev => ({
                      ...prev,
                      categories: prev.categories.map(c =>
                        c.id === cat.id
                          ? {
                              ...c,
                              items: c.items.map(i =>
                                i.id === item.id
                                  ? { ...i, description: e.target.value }
                                  : i
                              ),
                            }
                          : c
                      ),
                    }))
                  }
                  placeholder="Description (optional)"
                />

                {!isEditing && (
                  <button
                    style={styles.editBtn}
                    onClick={() =>
                      setEditingItem({ categoryId: cat.id, itemId: item.id })
                    }
                  >
                    Edit
                  </button>
                )}

                {isEditing && (
                  <>
                    <button
                      style={styles.saveBtn}
                      onClick={() => saveItem(cat.id, item)}
                    >
                      Save
                    </button>
                    <button
                      style={styles.cancelBtn}
                      onClick={() => setEditingItem(null)}
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            );
          })}

          <button style={styles.addBtn} onClick={() => addItem(cat.id)}>
            + Add item
          </button>
        </div>
      ))}

      <div style={styles.card}>
        <input
          style={styles.input}
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          placeholder="New category"
        />
        <button style={styles.addBtn} onClick={addCategory}>
          Add category
        </button>
      </div>
    </div>
  );
}

// STYLES
const styles = {
  page: { maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif" },
  card: {
    background: "#fff",
    padding: 16,
    borderRadius: 12,
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    marginBottom: 20,
  },
  itemRow: {
    display: "flex",
    gap: 10,
    marginBottom: 10,
    flexWrap: "wrap",
    alignItems: "center",
  },
  input: { flex: 1, padding: 10, borderRadius: 8, border: "1px solid #ccc" },
  price: { width: 100, padding: 10, borderRadius: 8, border: "1px solid #ccc" },
  addBtn: {
    marginTop: 10,
    padding: "8px 12px",
    borderRadius: 8,
    border: "none",
    background: "#1a73e8",
    color: "#fff",
    cursor: "pointer",
  },
  editBtn: {
    background: "#fbbc05",
    border: "none",
    padding: "6px 10px",
    borderRadius: 6,
    cursor: "pointer",
    color: "#fff",
  },
  saveBtn: {
    background: "#34a853",
    border: "none",
    padding: "6px 10px",
    borderRadius: 6,
    cursor: "pointer",
    color: "#fff",
  },
  cancelBtn: {
    background: "#ea4335",
    border: "none",
    padding: "6px 10px",
    borderRadius: 6,
    cursor: "pointer",
    color: "#fff",
  },
};
