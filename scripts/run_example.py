from review_patch import review_patch_with_rag

patch = """@@ -12,7 +12,13 @@ async function processUsers(userIds) {
   for (const id of userIds) {
-    const user = await getUserFromDB(id);
-    results.push(user);
+    try {
+      const user = await getUserFromDB(id);
+      if (!user) {
+        console.error("User not found:", id);
+      } else {
+        results.push(user);
+      }
+    } catch (err) {
+      console.error("Error fetching user:", err);
+    }
   }
   return results;
 }"""
response = review_patch_with_rag(patch)
print("\nIntelligent Review JSON:\n")
print(response)
