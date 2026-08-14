const fs = require('fs');
const path = require('path');

const dir = '/home/ruzz/projects/github/client-projects/weldtrack/weldtrackfrontend/src/views/dashboard/components/admin';
const files = [
  'AdminUsers.vue',
  'InventoryManagement.vue',
  'ServiceManagement.vue',
  'PayrollManagement.vue',
  'BookingApproval.vue'
];

for (const file of files) {
  const filePath = path.join(dir, file);
  if (!fs.existsSync(filePath)) continue;
  let content = fs.readFileSync(filePath, 'utf8');

  // 1. Modify the <th> with Actions
  // We look for Actions</th> or Status & Actions</th>
  content = content.replace(
    /(<th[^>]*text-right[^>]*>)(Status\s*&\s*Actions|Actions)(<\/th>)/,
    (match, p1, p2, p3) => {
      // Add sticky classes
      const newClassAttr = ' sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]"';
      let newP1 = p1.replace(/"\s*>/, newClassAttr + '>');
      if (newP1 === p1) { // If it didn't match the end quote properly, just replace >
         newP1 = p1.replace(/>$/, ' sticky right-0 z-10 bg-slate-50 dark:bg-slate-800 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">');
      }
      return newP1 + p2 + p3;
    }
  );

  // 2. Modify the <tr> in the tbody to have 'group' class
  // It usually looks like <tr v-for="..." class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50 ...">
  // We need to add 'group' to its class list.
  // Be careful not to replace tr in thead. The tr in tbody has v-for or is just after a comment.
  content = content.replace(
    /(<tbody[^>]*>[\s\S]*?<tr[^>]+class="[^"]*transition-colors[^"]*)(")/g,
    '$1 group"'
  );

  // 3. Modify the last <td> containing the buttons (or just the one with text-right and actions in its row, or the last td before </tr>)
  // We'll find the <td that contains the actions or is right-aligned in those files.
  // Actually, we can just replace the <td for the actions. In Vue files, it's often the one with class containing "whitespace-nowrap" or "text-right" right before </tr>.
  // To be safe, let's replace the last <td in the loop.
  // Let's match `<td class="px-... ">` and inject the sticky classes.
  // The easiest is to use a regex that finds `<td` and its classes, if it's followed by the action buttons.
  // Or simply replace the exact `td` classes we know are there.
  
  // AdminUsers: `<td class="px-5 py-4 text-right">`
  content = content.replace(
    /<td class="px-5 py-4 text-right">/g,
    '<td class="px-5 py-4 text-right sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50/50 dark:group-hover:bg-slate-800/50 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">'
  );

  // Inventory, Service, Payroll: `<td class="px-6 py-4 whitespace-nowrap">\s*<div class="flex (gap-3 )?justify-end( gap-3)?">`
  content = content.replace(
    /<td class="px-6 py-4 whitespace-nowrap">(\s*<div class="flex (?:gap-3 )?justify-end(?: gap-\d+)?">)/g,
    '<td class="px-6 py-4 whitespace-nowrap sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50/50 dark:group-hover:bg-slate-800/50 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">$1'
  );

  // BookingApproval: `<td class="px-5 py-5 text-right">`
  content = content.replace(
    /<td class="px-5 py-5 text-right">/g,
    '<td class="px-5 py-5 text-right sticky right-0 z-10 bg-white dark:bg-slate-900 group-hover:bg-slate-50/70 dark:group-hover:bg-slate-800/40 shadow-[-12px_0_15px_-4px_rgba(0,0,0,0.05)]">'
  );
  
  // Payroll: wait, Payroll has `<td class="px-6 py-4 whitespace-nowrap">\s*<div class="flex justify-end gap-3">` which matches the above.
  
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`Updated ${file}`);
}
