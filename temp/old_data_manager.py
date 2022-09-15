

    def basic_query(self, table, payload, first=False):
        result = self.session.query(table).filter_by(**payload).all()
        if first:
            return result[0]
        return result

    def check_object_in_db(self, table, payload):
        result = self.basic_query(table, payload)
        if len(result) > 1:
            raise ValueError(
                "[_object_was_found]: Length of result exceeded '1'.")
        if len(result) > 0:
            return True, result[0]
        return False, None

    def add_store(self, **kwargs):
        check, store = self.check_object_in_db(
            table=Store,
            payload={"name": kwargs['name']})

        if not check:
            store_chain = self.basic_query(
                table=StoreChain,
                payload={"name": kwargs['chain']},
                first=True)
            store = create_store(store_chain=store_chain, **kwargs)
            if self.database_add(obj=store):
                self.temp_cache["store"] = store
                return True
            raise NotImplementedError(
                "[add_store]: Store could not be added into database.")
        return False

    def add_location(self, **kwargs):
        location = create_location(store=self.temp_cache["store"], **kwargs)
        del self.temp_cache["store"]
        if not self.database_add(obj=location):
            raise NotImplementedError("[add_store]: Store location could not",
                                      "be added into database.")

    def add_product(self, **kwargs):
        check, product = self.check_object_in_db(
            table=Product,
            payload={"name": kwargs['name']})

        if not check:
            product = create_product(**kwargs)
            if not self.database_add(obj=product):
                raise NotImplementedError(
                    "[add_product]: Product could not be added into database.")
        self.temp_cache["product"] = product

    def add_store_product(self, **kwargs):
        product = self.temp_cache["product"]
        del self.temp_cache["product"]
        product_check = False
        store_check, store = self.check_object_in_db(
            table=Store,
            payload={"name": kwargs['store_name']})

        if store_check:
            product_check, store_product = self.check_object_in_db(
                table=StoreProduct,
                payload={"store_id": store.id, "product_ean": product.ean})
        else:
            print(
                f"[add_store_product]: {kwargs['store_name']} was not found.",
                f"\nStore product: {kwargs['name']} will not be added.")
            return False

        if product_check:
            return True

        store_product = create_store_product(store=store, **kwargs)
        store_product.product = product
        store.products.append(store_product)
        return True

    def init_chains(self):
        chain_names = ["s-market", "prisma", "sale", "alepa", "abc"]
        for chain in chain_names:
            self.session.add(StoreChain(chain))
        self.session.commit()

    def database_add(self, obj, commit=False):
        try:
            self.session.add(obj)
            if commit:
                self.session.commit()
            return True
        except SQLAlchemyError:
            return False

    def database_remove(self):
        pass
