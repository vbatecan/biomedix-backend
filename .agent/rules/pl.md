---
trigger: always_on
---

---

You are an expert in TypeScript, Angular, and scalable web application development. You write functional, maintainable, performant, and accessible code following Angular and TypeScript best practices.
## TypeScript Best Practices
- Use strict type checking
- Prefer type inference when the type is obvious
- Avoid the `any` type; use `unknown` when type is uncertain
## Angular Best Practices
- Always use standalone components over NgModules
- Must NOT set `standalone: true` inside Angular decorators. It's the default in Angular v20+.
- Use signals for state management
- Implement lazy loading for feature routes
- Do NOT use the `@HostBinding` and `@HostListener` decorators. Put host bindings inside the `host` object of the `@Component` or `@Directive` decorator instead
- Use `NgOptimizedImage` for all static images.
  - `NgOptimizedImage` does not work for inline base64 images.
## Accessibility Requirements
- It MUST pass all AXE checks.
- It MUST follow all WCAG AA minimums, including focus management, color contrast, and ARIA attributes.
### Components
- Keep components small and focused on a single responsibility
- Use `input()` and `output()` functions instead of decorators
- Use `computed()` for derived state
- Set `changeDetection: ChangeDetectionStrategy.OnPush` in `@Component` decorator
- Prefer inline templates for small components
- Prefer Reactive forms instead of Template-driven ones
- Do NOT use `ngClass`, use `class` bindings instead
- Do NOT use `ngStyle`, use `style` bindings instead
- When using external templates/styles, use paths relative to the component TS file.
## State Management
- Use signals for local component state
- Use `computed()` for derived state
- Keep state transformations pure and predictable
- Do NOT use `mutate` on signals, use `update` or `set` instead
## Templates
- Keep templates simple and avoid complex logic
- Use native control flow (`@if`, `@for`, `@switch`) instead of `*ngIf`, `*ngFor`, `*ngSwitch`
- Use the async pipe to handle observables
- Do not assume globals like (`new Date()`) are available.
- Do not write arrow functions in templates (they are not supported).
## Services
- Design services around a single responsibility
- Use the `providedIn: 'root'` option for singleton services
- Use the `inject()` function instead of constructor injection



### B. Signal-Based Reactivity
Antigravity uses **Signals** as the primary state primitive to bypass Zone.js overhead.

* **State:** Use `signal<T>(initialValue)` for mutable state.
* **Derived State:** Use `computed()` for any value that depends on other signals.
* **Inputs/Outputs:** Use the new `input()` and `output()` APIs.
* **Rules:**
    1.  Avoid `effect()` for data transformations; use `computed()` instead.
    2.  Minimize the use of `BehaviorSubject` unless complex RxJS operators (like `switchMap`) are strictly required.

---

## 2. Python Backend Best Practices

### A. Ecosystem & Tooling
* **Linter/Formatter:** Use **Ruff**. It replaces Black, Isort, and Flake8.
* **Package Management:** Use `uv` or `poetry`.
* **Type Safety:** Strict `mypy` or `pyright` checks must pass on all PRs.

### B. Architecture
* **Framework:** FastAPI (Asynchronous by default).
* **Validation:** Pydantic v2. Use `BaseModel` for all request/response schemas.
* **Database:** Use `SQLAlchemy` (Async) or `Tortoise-ORM`. Ensure all I/O calls are awaited to prevent blocking the event loop.

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    username: str

@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Non-blocking database call
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalar_one()
```

# PrimeNG

> The Most Complete Angular UI Component Library

## Guides

- [Installation](https://primeng.org/installation): Setting up PrimeNG in an Angular CLI project.
- [Configuration](https://primeng.org/configuration): Application wide configuration for PrimeNG.
- [Styled Mode](https://primeng.org/theming/styled): Choose from a variety of pre-styled themes or develop your own.
- [Unstyled Mode](https://primeng.org/theming/unstyled): Theming PrimeNG with alternative styling approaches.
- [Icons](https://primeng.org/icons): PrimeIcons is the default icon library of PrimeNG with over 250 open source icons.
- [Custom Icons](https://primeng.org/customicons): Use custom icons with PrimeNG components.
- [Pass Through](https://primeng.org/passthrough): Pass Through Props allow direct access to the underlying elements for complete customization.
- [Tailwind CSS](https://primeng.org/tailwind): Integration between PrimeNG and Tailwind CSS.
- [LLMs.txt](https://primeng.org/llms): LLM-optimized documentation endpoints for PrimeNG components.
- [MCP Server](https://primeng.org/mcp): Model Context Protocol (MCP) server for PrimeNG component library.
- [Accessibility](https://primeng.org/guides/accessibility): PrimeNG has WCAG 2.1 AA level compliance.
- [Animations](https://primeng.org/guides/animations): Built-in CSS animations for PrimeNG components.
- [RTL](https://primeng.org/guides/rtl): Right-to-left support for PrimeNG components.
- [Migration v19](https://primeng.org/migration/v19): Migration guide to PrimeNG v19.
- [Migration v20](https://primeng.org/migration/v20): Migration guide to PrimeNG v20.
- [Migration v21](https://primeng.org/migration/v21): Migration guide to PrimeNG v21.

## Components

- [Angular Accordion Component](https://primeng.org/accordion): Accordion groups a collection of contents in tabs.
- [Angular Animate On Scroll Directive](https://primeng.org/animateonscroll): AnimateOnScroll is used to apply animations to elements when entering or leaving the viewport during scrolling.
- [Angular AutoComplete Component](https://primeng.org/autocomplete): AutoComplete is an input component that provides real-time suggestions when being typed.
- [Angular AutoFocus Directive](https://primeng.org/autofocus): AutoFocus manages focus on focusable element on load.
- [Angular Avatar Component](https://primeng.org/avatar): Avatar represents people using icons, labels and images.
- [Angular Badge Component](https://primeng.org/badge): Badge is a small status indicator for another element.
- [Angular BlockUI Component](https://primeng.org/blockui): BlockUI can either block other components or the whole page.
- [Angular Breadcrumb Component](https://primeng.org/breadcrumb): Breadcrumb provides contextual information about page hierarchy.
- [Angular Button Component](https://primeng.org/button): Button is an extension to standard button element with icons and theming.
- [Angular Card Component](https://primeng.org/card): Card is a flexible container component.
- [Angular Carousel Component](https://primeng.org/carousel): Carousel is a content slider featuring various customization options.
- [Angular CascadeSelect Component](https://primeng.org/cascadeselect): CascadeSelect displays a nested structure of options.
- [Angular Chart Component](https://primeng.org/chart): Chart components are based on Charts.js 3.3.2+, an open source HTML5 based charting library.
- [Angular Checkbox Component](https://primeng.org/checkbox): Checkbox is an extension to standard checkbox element with theming.
- [Angular Chip Component](https://primeng.org/chip): Chip represents entities using icons, labels and images.
- [Angular ColorPicker Component](https://primeng.org/colorpicker): ColorPicker is an input component to select a color.
- [Angular ConfirmDialog Component](https://primeng.org/confirmdialog): ConfirmDialog is backed by a service utilizing Observables to display confirmation windows easily that can be shared by multiple actions on the same component.
- [Angular ConfirmPopup Component](https://primeng.org/confirmpopup): ConfirmPopup displays a confirmation overlay displayed relatively to its target.
- [Angular ContextMenu Component](https://primeng.org/contextmenu): ContextMenu displays an overlay menu on right click of its target.
- [Angular DataView Component](https://primeng.org/dataview): DataView displays data in grid grid-cols-12 gap-4 or list layout with pagination and sorting features.
- [Angular DatePicker Component](https://primeng.org/datepicker): DatePicker is an input component to select a date.
- [Angular Dialog Component](https://primeng.org/dialog): Dialog is a container to display content in an overlay window.
- [Angular Divider Component](https://primeng.org/divider): Divider is used to separate contents.
- [Angular Dock Component](https://primeng.org/dock): Dock is a navigation component consisting of menuitems.
- [Angular Drag and Drop Component](https://primeng.org/dragdrop): pDraggable and pDroppable directives apply drag-drop behaviors to any element.
- [Angular Drawer Component](https://primeng.org/drawer): Drawer is a container component displayed as an overlay.
- [Angular Dynamic Dialog Component](https://primeng.org/dynamicdialog): Dialogs can be created dynamically with any component as the content using a DialogService.
- [Angular Editor Component](https://primeng.org/editor): Editor is rich text editor component based on Quill.
- [Angular Fieldset Component](https://primeng.org/fieldset): Fieldset is a grouping component with a content toggle feature.
- [Angular FileUpload Component](https://primeng.org/fileupload): FileUpload is an advanced uploader with dragdrop support, multi file uploads, auto uploading, progress tracking and validations.
- [Angular Float Label Component](https://primeng.org/floatlabel): FloatLabel appears on top of the input field when focused.
- [Angular Fluid Component](https://primeng.org/fluid): Fluid is a layout component to make descendant components span full width of their container.
- [Angular Focus Trap Component](https://primeng.org/focustrap): Focus Trap keeps focus within a certain DOM element while tabbing.
- [Angular Gallery Component](https://primeng.org/galleria): Galleria is an advanced content gallery component.
- [Angular IconField Component](https://primeng.org/iconfield): IconField wraps an input and an icon.
- [Angular Ifta Label Component](https://primeng.org/iftalabel): IftaLabel is used to create infield top aligned labels.
- [Angular ImageCompare Component](https://primeng.org/imagecompare): Compare two images side by side with a slider.
- [Angular Inplace Component](https://primeng.org/inplace): Inplace provides an easy to do editing and display at the same time where clicking the output displays the actual content.
- [Angular InputGroup Component](https://primeng.org/inputgroup): Text, icon, buttons and other content can be grouped next to an input.
- [Angular InputMask Component](https://primeng.org/inputmask): InputMask component is used to enter input in a certain format such as numeric, date, currency and phone.
- [Angular InputNumber Component](https://primeng.org/inputnumber): InputNumber is an input component to provide numerical input.
- [Angular InputText Component](https://primeng.org/inputtext): InputText is 